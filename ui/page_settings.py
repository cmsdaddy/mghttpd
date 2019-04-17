from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
from django.urls import path
import os
import ui.mg as mg
import random
import ui.api as api
import time
import json
import codecs
import ui.configure
import codecs


class SettingsItemBasic(object):
    """配置项基类"""
    def __init__(self, **kwargs):
        self.cls = kwargs['cls']
        self.name = kwargs['name']
        self.default = kwargs['default']
        self.value = kwargs['default']
        self.path = kwargs['path']
        self.help_text = kwargs['help_text'] if 'help_text' in kwargs else ''

        path = self.fetch_json_path()
        if os.path.exists(path):
            self.value = self.load()
        else:
            self.save(self.value)

    def fetch_json_path(self):
        """获取当前数据点的json文件保存路径"""
        father = "".join(['data/configure/', self.cls.title])
        if os.path.exists(father) is False:
            os.makedirs(father)

        path = "".join(['data/configure/', self.cls.title, '/', self.name, '.json'])
        return path

    def load(self, path=None):
        """从配置文件中加载数据"""
        if path is None:
           path = self.fetch_json_path()

        with codecs.open(path, encoding='utf8') as file:
            value = json.load(file)

        return value

    def save(self, value, path=None):
        """将值保存到配置文件中"""
        if path is None:
           path = self.fetch_json_path()

        self.value = value
        with codecs.open(path, 'w', encoding='utf8') as file:
            json.dump(value, file)

        if self.path is None:
            return

        self.sync()

    def sync(self):
        """将值同步到数据总线上"""
        if self.path is None:
            return

        if self.path[0] == '/':
            databus_path = '/系统配置参数' + self.path
        else:
            databus_path = '/系统配置参数/' + self.path

        host = mg.get_datacenter_address()
        path = mg.get_datacenter_root() + databus_path
        '''
        X = api.api_read(host, path)

        if X is None:
            return None
        '''

        print("sync", host, path, self.value)
        return api.api_write(host, path, self.value)

    def complie(self, txt):
        """返回指定格式的数据"""
        if isinstance(self.value, int):
            return int(txt)
        elif isinstance(self.value, str):
            return txt
        else:
            raise TypeError("support int and str only.")


class SIntegerItem(SettingsItemBasic):
    """整数配置项"""
    def __init__(self, **kwargs):
        super(SIntegerItem, self).__init__(**kwargs)
        self.max_value = kwargs['max'] if 'max' in kwargs else 2147483647
        self.min_value = kwargs['min'] if 'min' in kwargs else -2147483647
        self.html_template = '<div class="input-group input-group-sm">\n'\
                             '  <span class="input-group-addon">%s</span>\n'\
                             '  <input type="number" class="form-control" min="%d" max="%d" name="%s" value="%d">\n'\
                             '</div>\n'

    def __str__(self):
        """返回html内容"""
        return self.html_template % (self.name, self.min_value, self.max_value, self.name, self.value)


class STextItem(SettingsItemBasic):
    """文本配置项"""
    def __init__(self, **kwargs):
        super(STextItem, self).__init__(**kwargs)
        self.html_template = '<div class="input-group input-group-sm">\n'\
                             '  <span class="input-group-addon">%s</span>\n'\
                             '  <input type="text" class="form-control" name="%s" value="%s">\n'\
                             '</div>\n'

    def __str__(self):
        """返回html内容"""
        return self.html_template % (self.name, self.name, self.value)


class SRadiosItem(SettingsItemBasic):
    """单选配置项"""
    def __init__(self, **kwargs):
        super(SRadiosItem, self).__init__(**kwargs)
        self.radios = kwargs['radios']
        self.template = '<label class="checkbox-inline"><input type="radio" name="%s" value="%s" %s>%s</label>\n'

    def __str__(self):
        """返回html内容"""
        html_list = ['<lable>', self.name]
        for lable, value in self.radios.items():
            if value == self.value:
                html = self.template % (self.name, str(value), 'checked', lable)
            else:
                html = self.template % (self.name, str(value), '', lable)
            html_list.append(html)
        html_list.append('</lable>')
        return "".join(html_list)


class SSelectItem(SettingsItemBasic):
    """下拉框配置项"""
    def __init__(self, **kwargs):
        super(SSelectItem, self).__init__(**kwargs)
        self.selector = kwargs['selector']
        self.template = '  <option value="%s" %s>%s</option>\n'

    def __str__(self):
        """返回html内容"""
        html_list = ['<lable>%s: <select name="%s" style="height: 25px; min-width: 100px;">\n' % (self.name, self.name)]
        for lable, value in sorted(self.selector.items(), key=lambda d:d[0]):
            if value == self.value:
                html = self.template % (str(value), 'selected', lable)
            else:
                html = self.template % (str(value), '', lable)
            html_list.append(html)
        html_list.append('</select></lable>\n')
        return "".join(html_list)


class GroupInLineItem:
    """参数配置组"""
    
    def __init__(self, **kwargs):
        self.groups = kwargs['groups']

    def __str__(self):
        """返回html内容"""
        count = len(self.groups)
        if count in {1, 2, 3, 4, 6, 12}:
            col_width = 'col-xs-%d' % (12 / count)
        elif count > 6 and count < 12:
            col_width = 'col-xs-1'
        elif count == 5:
            col_width = 'col-xs-2'
        else:
            raise ValueError("row supported {1, 2, 3, 4, 6, 12} only")

        html_list = list()
        for group in self.groups:
            html = "".join(['<div class="%s">\n' % col_width, str(group), '</div>\n'])
            html_list.append(html)

        return "".join(html_list)


class SplitLine:
    """分隔符"""
    def __str__(self):
        """返回html内容"""
        return "<hr>"


class BlankLine:
    """空行"""
    def __str__(self):
        """返回html内容"""
        return ""


class PosterProcessor(object):
    """提交页面处理对象"""
    def __init__(self, title):
        self.title = title
        #self.items_list = list()
        #self.imap = dict()

    def on_post(self, request):
        """处理更改事件"""
        for name, value in request.POST.items():
            item = self.imap[name]
            real = item.complie(value)
            if real != item.value:
                print("change", name, 'from', item.value, 'to', real)
                item.save(real)

    def sync(self):
        '''
        try:
            items_list = self.imap.items()
            for key, item in items_list:
                print(key, item.path)
        except Exception as e:
            print(e)
        '''
        for name, item in self.imap.items():
            item.sync()


class 监控通讯参数(PosterProcessor):
    """监控通讯参数配置对象"""
    def __init__(self):
        super(监控通讯参数, self).__init__(self.__class__.__name__)
        imap = dict()

        imap['数据中心地址'] = STextItem(cls=self, name='数据中心地址', default='192.168.2.106', path=None)
        imap['SOCKET协议端口'] = SIntegerItem(cls=self, name='SOCKET协议端口', default=8084, path=None)
        imap['HTTP协议端口'] = SIntegerItem(cls=self, name='HTTP协议端口', default=8083, path=None)
        imap['协议版本'] = SRadiosItem(cls=self, name='协议版本', default='v1.0', path=None,
                                          radios={" v1.0": "v1.0"})

        imap['UI服务器地址'] = STextItem(cls=self, name='UI服务器地址', default='127.0.0.1', path=None)
        imap['UI服务端口'] = SIntegerItem(cls=self, name='UI服务端口', default=8000, path=None)

        self.imap = imap
        self.items_list = [
            GroupInLineItem(groups=[imap['数据中心地址'], imap['SOCKET协议端口'],
                                           imap['HTTP协议端口'], imap['协议版本']]),
            GroupInLineItem(groups=[imap['UI服务器地址'], imap['UI服务端口']]),
        ]


class 云平台参数(PosterProcessor):
    """云平台参数配置对象"""
    def __init__(self):
        super(云平台参数, self).__init__(self.__class__.__name__)
        imap = dict()
        imap['云平台地址'] = STextItem(cls=self, name='云平台地址', default='', path=None)
        imap['HTTP协议端口'] = SIntegerItem(cls=self, name='HTTP协议端口', default=8084, path=None)
        imap['协议版本'] = SRadiosItem(cls=self, name='协议版本', default='v1.0', path=None,
                                          radios={" v1.0": "v1.0"})

        imap['站点名称'] = STextItem(cls=self, name='站点名称', default='127.0.0.1', path=None)
        imap['站点地址'] = STextItem(cls=self, name='站点地址', default="杭州市莫干山路209号", path=None)
        imap['站点类型'] = SSelectItem(cls=self, name='站点类型', default="光伏储能", path=None,
                                          selector={" 光伏储能": "光伏储能", "光储站点": "光储站点", "分布式": "分布式"})

        self.imap = imap
        self.items_list = [
            GroupInLineItem(groups=[imap['云平台地址'], imap['HTTP协议端口'], imap['协议版本']]),
            GroupInLineItem(groups=[imap['站点名称'], imap['站点地址'], imap['站点类型']])
        ]


class 外设数量参数(PosterProcessor):
    """外设数量参数参数配置对象"""
    def __init__(self):
        super(外设数量参数, self).__init__(self.__class__.__name__)
        imap = dict()
        imap['BMS设备数量'] = SIntegerItem(cls=self, name='BMS设备数量', default=1, path='/BMS设备数量/')
        imap['PCS设备数量'] = SIntegerItem(cls=self, name='PCS设备数量', default=1, path='/PCS设备数量/')
        imap['PCC设备数量'] = SIntegerItem(cls=self, name='PCC设备数量', default=0, path='/PCC设备数量/')
        imap['光伏逆变器数量'] = SIntegerItem(cls=self, name='光伏逆变器数量', default=0, path='/逆变器设备数量/')
        imap['空调设备数量'] = SIntegerItem(cls=self, name='空调设备数量', default=0, path='/空调设备数量/')

        imap['开入开出盒数量'] = SIntegerItem(cls=self, name='开入开出盒数量', default=0, path='/开关量协议盒设备数量/')

        self.imap = imap
        self.items_list = [
            imap['BMS设备数量'],
            imap['PCS设备数量'],
            imap['PCC设备数量'],
            imap['空调设备数量'],

            imap['光伏逆变器数量'],
            imap['开入开出盒数量'],
        ]


class 系统通用参数(PosterProcessor):
    """系统通用参数配置对象"""
    def __init__(self):
        super(系统通用参数, self).__init__(self.__class__.__name__)
        imap = dict()
        radios = {"列表": "列表", "鱼骨图": "鱼骨图"}
        imap['历史故障显示方式'] = SRadiosItem(cls=self, name='历史故障显示方式', default='列表', path=None, radios=radios)
        imap['历史事件显示方式'] = SRadiosItem(cls=self, name='历史事件显示方式', default='列表', path=None, radios=radios)

        self.imap = imap
        self.items_list = [
            imap['历史故障显示方式'],
            imap['历史事件显示方式']
        ]


class SUB_BMS参数(PosterProcessor):
    def __init__(self, bmsid):
        super(SUB_BMS参数, self).__init__('BMS参数/%d' % bmsid)
        imap = dict()

        bms_selector = {"高特": "高特", "钜威": "钜威", "科工": "科工", "日升企标": "日升企标"}

        path = '/BMS设备通讯地址/%d/' % bmsid
        name = '通讯地址-%d' % bmsid
        imap[name] = STextItem(cls=self, name=name, default="", path=path)

        path = '/BCMU设备数量/%d/' % bmsid
        name = 'BCMU数量-%d' % bmsid
        imap[name] = SIntegerItem(cls=self, name=name, default=1, path=path)

        path = '/BCMU设备电池数量/%d/' % bmsid
        name = '电池数量-%d' % bmsid
        imap[name] = SIntegerItem(cls=self, name=name, default=0, path=path)

        path = '/BMS设备型号/%d/' % bmsid
        name = '型号-%d' % bmsid
        imap[name] = SSelectItem(cls=self, name=name, default="未配置", path=path, selector=bms_selector)

        path = '/BMS总容量/%d/' % bmsid
        name = '容量-%d' % bmsid
        imap[name] = SIntegerItem(cls=self, name=name, default=0, path=path)

        self.imap = imap
        groups = [imap['通讯地址-%d' % bmsid], imap['型号-%d' % bmsid]]

        self.items_list = [
            GroupInLineItem(groups=groups),
            imap['BCMU数量-%d' % bmsid],
            imap['电池数量-%d' % bmsid],
            imap['容量-%d' % bmsid]
        ]


class BMS参数(PosterProcessor):
    """BMS参数配置对象"""
    have_children = True
    children_id_list = [bmsid for bmsid in range(16)]

    def __init__(self, bmsid):
        super(BMS参数, self).__init__(self.__class__.__name__)
        self.items_list = list()
        self.imap = dict()
        self.subid = bmsid

        bms = SUB_BMS参数(bmsid=bmsid)
        self.items_list.extend(bms.items_list)
        self.imap = dict(self.imap, **bms.imap)


class EMS_Settings(PosterProcessor):
    """EMS通讯参数配置对象"""
    def __init__(self):
        super().__init__(self.__class__.__name__)
        imap = dict()
        imap['EMS输出端口'] = SIntegerItem(cls=self, name='EMS输出端口', default=8084, path="/EMS输出端口/")
        imap['EMS设备地址'] = STextItem(cls=self, name='EMS设备地址', default='192.168.2.106', path="/EMS模块通讯地址/")
        imap['EMS子网掩码'] = STextItem(cls=self, name='EMS子网掩码', default='255.255.255.0', path=None)
        imap['EMS网关'] = STextItem(cls=self, name='EMS网关', default="192.168.1.1", path=None)

        self.imap = imap
        self.items_list = [
            GroupInLineItem(groups=[imap['EMS输出端口']]),
            GroupInLineItem(groups=[imap['EMS设备地址'], imap['EMS子网掩码'], imap['EMS网关']]),
        ]

    def on_post(self, request):
        old_ip = self.imap['EMS设备地址'].value
        old_mask = self.imap['EMS子网掩码'].value
        old_gateway = self.imap['EMS网关'].value

        super().on_post(request)

        new_ip = self.imap['EMS设备地址'].value
        new_mask = self.imap['EMS子网掩码'].value
        new_gateway = self.imap['EMS网关'].value

        if {old_ip, old_mask, old_gateway} ^ {new_ip, new_mask, new_gateway} == set({}):
            print("no change.")
            return

        command_line_list = [
            "curl -s ",
            "'http://", new_ip, ":8085",
            "/config/?",
            "ip=", new_ip,
            "&netmask=", new_mask,
            "&gateway=", new_gateway,
            "'&"
        ]
        comand_line = "".join(command_line_list)
        print("changed", comand_line)
        os.system(comand_line)


class SUB_PCS参数(PosterProcessor):
    def __init__(self, pcsid):
        super(SUB_PCS参数, self).__init__('PCS参数/%d' % pcsid)
        imap = dict()

        self.imap = imap
        pcs_selector = {"阳光": "阳光", "盛宏":"盛宏", "日升企标": "日升企标"}

        path = '/PCS设备通讯地址/%d/' % pcsid
        imap['通讯地址-%d' % pcsid] = STextItem(cls=self, name='通讯地址-%d' % pcsid, default="", path=path)

        path = '/PCS设备型号/%d/' % pcsid
        imap['型号-%d' % pcsid] = SSelectItem(cls=self, name='型号-%d' % pcsid, default="未配置", path=path,
                                            selector=pcs_selector)

        groups = [imap['通讯地址-%d' % pcsid], imap['型号-%d' % pcsid]]
        self.items_list = [
            GroupInLineItem(groups=groups)
        ]


class PCS参数(PosterProcessor):
    """PCS参数配置对象"""
    def __init__(self):
        super(PCS参数, self).__init__(self.__class__.__name__)
        self.items_list = list()
        self.imap = dict()

        for i in range(16):
            pcs = SUB_PCS参数(pcsid=i)
            self.items_list.extend(pcs.items_list)
            self.imap = dict(self.imap, **pcs.imap)


class SUB_INV参数(PosterProcessor):
    def __init__(self, invid):
        super(SUB_INV参数, self).__init__('INV参数/%d' % invid)
        imap = dict()

        self.imap = imap
        inv_selector = {"阳光": "阳光", "未配置": "未配置"}

        path = '/逆变器设备通讯地址/%d/' % invid
        imap['通讯地址-%d' % invid] = STextItem(cls=self, name='通讯地址-%d' % invid, default="", path=path)

        path = '/逆变器设备型号/%d/' % invid
        imap['型号-%d' % invid] = SSelectItem(cls=self, name='型号-%d' % invid, default="未配置", path=path,
                                            selector=inv_selector)

        groups = [imap['通讯地址-%d' % invid], imap['型号-%d' % invid]]
        self.items_list = [
            GroupInLineItem(groups=groups)
        ]


class INV参数(PosterProcessor):
    """INV参数配置对象"""
    def __init__(self):
        super(INV参数, self).__init__(self.__class__.__name__)
        imap = dict()
        self.items_list = list()
        self.imap = dict()

        for i in range(16):
            inv = SUB_INV参数(invid=i)
            self.items_list.extend(inv.items_list)
            self.imap = dict(self.imap, **inv.imap)


class SUB_空调参数(PosterProcessor):
    def __init__(self, airid):
        super(SUB_空调参数, self).__init__('空调参数/%d' % airid)
        imap = dict()

        self.imap = imap
        air_selector = {"未配置": "未配置", "英维克": "英维克"}

        path = '/空调设备通讯地址/%d/' % airid
        imap['通讯地址-%d' % airid] = STextItem(cls=self, name='通讯地址-%d' % airid, default="", path=path)

        path = '/空调设备型号/%d/' % airid
        imap['型号-%d' % airid] = SSelectItem(cls=self, name='型号-%d' % airid, default="未配置", path=path,
                                            selector=air_selector)

        groups = [imap['通讯地址-%d' % airid], imap['型号-%d' % airid]]
        self.items_list = [
            GroupInLineItem(groups=groups)
        ]

class SUB_消防参数(PosterProcessor):
    def __init__(self, airid):
        super(SUB_消防参数, self).__init__('消防参数/%d' % airid)
        imap = dict()

        self.imap = imap
        air_selector = {"未配置": "未配置", "能启能": "能启能"}

        path = '/空调设备通讯地址/%d/' % airid
        imap['通讯地址-%d' % airid] = STextItem(cls=self, name='通讯地址-%d' % airid, default="", path=path)

        path = '/空调设备型号/%d/' % airid
        imap['型号-%d' % airid] = SSelectItem(cls=self, name='型号-%d' % airid, default="未配置", path=path,
                                            selector=air_selector)

        groups = [imap['通讯地址-%d' % airid], imap['型号-%d' % airid]]
        self.items_list = [
            GroupInLineItem(groups=groups)
        ]

class 空调参数(PosterProcessor):
    """空调参数配置对象"""
    def __init__(self):
        super(空调参数, self).__init__(self.__class__.__name__)
        imap = dict()
        self.items_list = list()
        self.imap = dict()

        for i in range(16):
            air = SUB_空调参数(airid=i)
            self.items_list.extend(air.items_list)
            self.imap = dict(self.imap, **air.imap)

class 消防参数(PosterProcessor):
    """消防参数配置对象"""
    def __init__(self):
        super(消防参数, self).__init__(self.__class__.__name__)
        imap = dict()
        self.items_list = list()
        self.imap = dict()

        for i in range(16):
            air = SUB_消防参数(airid=i)
            self.items_list.extend(air.items_list)
            self.imap = dict(self.imap, **air.imap)

class 电池参数(PosterProcessor):
    """电池数量参数配置对象"""
    def __init__(self):
        super(电池参数, self).__init__(self.__class__.__name__)
        imap = dict()
        self.items_list = list()
        self.imap = dict()

        bat_selector = {"磷酸铁锂": "磷酸铁锂", "铅酸": "铅酸", "铅炭": "铅炭"}
        imap['电芯材质'] = SSelectItem(cls=self, name='电芯材质', default='磷酸铁锂', path=None, selector=bat_selector)
        imap['单体额定电压(mV)'] = SIntegerItem(cls=self, name='单体额定电压(mV)', default=3300, path=None)
        imap['单体容量(A.H)'] = SIntegerItem(cls=self, name='单体容量(A.H)', default=30, path=None)

        path = '/单簇pack串联数/'
        imap['单簇pack串联数'] = SIntegerItem(cls=self, name='单簇pack串联数', default=16, path=path)

        path = '/pack内置温度采样点个数/'
        imap['pack内置温度采样点个数'] = SIntegerItem(cls=self, name='pack内置温度采样点个数', default=4, path=None)

        self.imap = imap
        self.items_list.extend([
            imap['电芯材质'],
            GroupInLineItem(groups=[imap['单体额定电压(mV)'], imap['单体容量(A.H)']]),
            GroupInLineItem(groups=[imap['单簇pack串联数'], imap['pack内置温度采样点个数']])
        ])


class 开入开出盒参数(PosterProcessor):
    """开入开出盒参数配置对象"""
    def __init__(self):
        super(开入开出盒参数, self).__init__(self.__class__.__name__)
        imap = dict()
        self.items_list = list()
        self.imap = dict()

        in_selector_list = {
                "未定义",
                "主进线断路器位置",
                "备用进线断路器位置",
                "空调馈线断路器位置",
                "浪涌回路断路器位置",
                "UPS馈线断路器位置",
                "BMS馈线断路器位置",
                "消防馈线断路器位置",
                "视频馈线断路器位置",
                "控制电源断路器位置",
                "UPS检修断路器位置",
                "1#门位置",
                "2#门位置",
                "3#门位置",
                "消防启动信号",
                "消防手动启动信号",
                "消防手动停止信号",
                "系统急停信号",
                "BMS故障信号",
                "BMS故障待定1",
                "BMS故障待定2",
                "1#PACK断路器合位",
                "1#PACK断路器分位",
                "1#PACK断路器故障",
                "2#PACK断路器合位",
                "2#PACK断路器分位",
                "2#PACK断路器故障",
                "3#PACK断路器合位",
                "3#PACK断路器分位",
                "3#PACK断路器故障",
                "4#PACK断路器合位",
                "4#PACK断路器分位",
                "4#PACK断路器故障",
                "5#PACK断路器合位",
                "5#PACK断路器分位",
                "5#PACK断路器故障",
        }
        in_selector = {key: key for key in in_selector_list}
        out_selector = {
            "未定义": "未定义",
            "消防闭锁-": "消防闭锁-"
        }
        ain_selector_list = {
            "温度采集1",
            "温度采集2",
            "温度采集3",
            "温度采集4",
            "未定义"
        }
        ain_selector = {key: key for key in ain_selector_list}

        in_list = list()
        for i in range(48):
            path = '/开关量设置数据块/开关量输入%d/' % i
            name = '开关量输入%d' % i
            item = SSelectItem(cls=self, name=name, default='未定义', path=path, selector=in_selector)
            imap[name] = item
            in_list.append(item)

        out_list = list()
        for i in range(16):
            path = '/开关量设置数据块/开关量输出%d/' % i
            name = '开关量输出%d' % i
            item = SSelectItem(cls=self, name=name, default='未定义', path=path, selector=out_selector)
            imap[name] = item
            out_list.append(item)

        ain_list = list()
        for i in range(8):
            path = '/开关量设置数据块/模拟量输入%d/' % i
            name = '模拟量输入%d' % i
            item = SSelectItem(cls=self, name=name, default='未定义', path=path, selector=ain_selector)
            imap[name] = item
            ain_list.append(item)

        self.imap = imap
        self.items_list = [
            GroupInLineItem(groups=in_list[0: 6]), GroupInLineItem(groups=in_list[6: 12]),
            GroupInLineItem(groups=in_list[12: 18]), GroupInLineItem(groups=in_list[18: 24]),
            GroupInLineItem(groups=in_list[24: 30]), GroupInLineItem(groups=in_list[30: 36]),
            GroupInLineItem(groups=in_list[36: 42]), GroupInLineItem(groups=in_list[42: 48]),
            BlankLine(),
            GroupInLineItem(groups=out_list[0: 4]), GroupInLineItem(groups=out_list[4: 8]),
            GroupInLineItem(groups=out_list[8: 12]), GroupInLineItem(groups=out_list[12: 16]),
            BlankLine(),
            GroupInLineItem(groups=ain_list[0: 4]), GroupInLineItem(groups=ain_list[4: 8])
        ]


class 配置数据准备好标识(PosterProcessor):
    """配置数据准备好标识配置对象"""
    def __init__(self):
        super(配置数据准备好标识, self).__init__(self.__class__.__name__)
        imap = dict()
        self.items_list = list()
        self.imap = dict()

        path = '/状态标志位/'
        imap['状态标志位'] = SIntegerItem(cls=self, name='状态标志位', default=1, path=path)

        self.imap = imap
        self.items_list = [imap['状态标志位']]


def show_autmatic_page(request, ProcessorClass):
    """显示可以自动配置的页面参数列表"""
    context = dict()
    try:
        have_children = ProcessorClass.have_children
    except:
        have_children = False

    if have_children is True:
        try:
            subid = int(request.GET['subid'])
        except:
            subid = 0
        x = ProcessorClass(subid)
    else:
        x = ProcessorClass()

    if request.method == 'POST':
        try:
            x.on_post(request)
        except Exception as e:
            return automatic_settings_deniend(code=500, path=request.path)
        return automatic_settings_accept(path=request.path)

    context['processor'] = x
    return render(request, "97-系统参数配置管理/base-自动生成配置页面.html", context=context)


def automatic_settings_accept(path):
    """参数设置值接受"""
    return HttpResponseRedirect("/error/formok/?code=0&next=%s" % path)


def automatic_settings_deniend(code, path):
    """参数设置值拒绝"""
    return HttpResponseRedirect("/error/formerror/?code=%d&next=%s" % (code, path))


# 将当前参数全都推送到数据总线
def refresh_system_configure(request):
    sub_class_list = PosterProcessor.__subclasses__()
    for SubClass in sub_class_list:

        # 子类不进行同步操作
        if SubClass.__name__.find('SUB_') == 0:
            continue

        if SubClass == 配置数据准备好标识:
            continue

        try:
            have_children = SubClass.have_children
        except:
            have_children = False

        if have_children is False:
            obj = SubClass()
            obj.sync()
        else:
            for subid in SubClass.children_id_list:
                obj = SubClass(subid)
                obj.sync()


    # 写入数据配置好标识
    ok = 配置数据准备好标识()
    ok.sync()

    return HttpResponse("ok")


# 配置页首页
def show_settings_warning_page(request):
    context = dict()
    context['request'] = request
    return render(request, "97-系统参数配置管理/系统参数配置警告.html", context=context)


urlpatterns = [
    path('', show_settings_warning_page),
    path('refresh/', refresh_system_configure),

    path('scada_com/', lambda request: show_autmatic_page(request, 监控通讯参数)),
    path('cloud/', lambda request: show_autmatic_page(request, 云平台参数)),
    path('peripheral/', lambda request: show_autmatic_page(request, 外设数量参数)),
    path('video/', lambda request: show_autmatic_page(request, 监控通讯参数)),
    path('firecontrol/', lambda request: show_autmatic_page(request, 消防参数)),
    path('airconditioner/', lambda request: show_autmatic_page(request, 空调参数)),
    path('gpio/', lambda request: show_autmatic_page(request, 开入开出盒参数)),

    # 通用设备配置页
    path('inv/', lambda request: show_autmatic_page(request, INV参数)),
    path('pcs/', lambda request: show_autmatic_page(request, PCS参数)),
    path('bms/', lambda request: show_autmatic_page(request, BMS参数)),

    path('ems/', lambda request: show_autmatic_page(request, EMS_Settings)),

    path('battery/', lambda request: show_autmatic_page(request, 电池参数)),
    path('report/', lambda request: show_autmatic_page(request, 监控通讯参数)),
    path('general/', lambda request: show_autmatic_page(request, 系统通用参数)),
    path('datetime/', lambda request: show_autmatic_page(request, 监控通讯参数)),
    path('password/', lambda request: show_autmatic_page(request, 监控通讯参数)),
    path('backup/', lambda request: show_autmatic_page(request, 监控通讯参数)),
    path('bell/', lambda request: show_autmatic_page(request, 监控通讯参数)),

    # 开发选项
    path('dev/autorun/', lambda request: show_autmatic_page(request, 监控通讯参数)),
    path('dev/collector/', lambda request: show_autmatic_page(request, 监控通讯参数)),
]
urls = (urlpatterns, "settings", "settings")
