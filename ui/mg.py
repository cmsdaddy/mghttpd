from urllib.request import *
import urllib
import urllib.parse
import json
import codecs
import ui.api as api


# 获取单体电池电压信息
def get_single_battery_V(heap_sn, group_sn, battery_count):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/BMS数据块/%d/BCMU单体电池电压/%d/单体电池电压/' % (heap_sn, group_sn)
    X = api.api_read(host, path)
    if X is None:
        return [0.000] * battery_count

    return [(round(v/1000, 3)) for v in X]


# 获取单体温度信息
def get_single_battery_T(heap_sn, group_sn, battery_count):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/BMS数据块/%d/BCMU单体电池温度/%d/单体电池温度/' % (heap_sn, group_sn)
    X = api.api_read(host, path)
    if X is None:
        return [0] * battery_count

    return [ "%d" % v for v in X ]


# 获取单体SOC信息
def get_single_battery_SOC(heap_sn, group_sn, battery_count):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/BMS数据块/%d/BCMU单体电池SOC/%d/单体电池SOC/' % (heap_sn, group_sn)
    X = api.api_read(host, path)
    if X is None:
        return [0] * battery_count

    return [v for v in X ]


# 获取单体SOH信息
def get_single_battery_SOH(heap_sn, group_sn, battery_count):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/BMS数据块/%d/BCMU单体电池SOH/%d/单体电池SOH/' % (heap_sn, group_sn)
    X = api.api_read(host, path)
    if X is None:
        return [0] * battery_count

    return [v for v in X ]


# 过滤黑名单中的遥调值
def filter_api_yaotiao(origin_dict, blacklist, column):
    output_items = []

    line = []
    x = 0
    origin_list = [(key, value) for key, value in origin_dict.items()]
    origin_list = sorted(origin_list)

    for key, value in origin_list:
        if key in blacklist:
            continue

        if key not in {"时间", "系统时钟"}:
            o = (key, value, '')
        else:
            value = "%04d%02d%02d%02d%02d%02d" % tuple(value)
            o = (key, value, '')
        line.append(o)

        if len(line) == column:
            output_items.append(line)
            line = []

    if len(line) > 0:
        output_items.append(line)

    return output_items


# 获取BMS的遥调值
def get_bms_yaotiao(heap_sn):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/BMS数据块/%d/BMS遥调信息/' % (heap_sn)
    X = api.api_read(host, path)

    if X is None:
        return {}

    return X


# 获取BMS电池组的遥测值
def get_bms_group_yaoce(heap_sn, group_sn):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/BMS数据块/%d/BCMU遥测信息/%d/' % (heap_sn, group_sn)
    X = api.api_read(host, path)

    if X is None:
        return {}

    return X


# 获取电池堆遥测值
def get_bms_heap_yaoce(heap_sn):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/BMS数据块/%d/BMS遥测信息/' % (heap_sn)
    X = api.api_read(host, path)

    if X is None:
        return {}

    return X


# 设置电池堆遥调, 变化的写入
def set_bms_heap_yaotiao(heap_sn, user_set_dict, visitor=None):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/BMS数据块/%d/BMS遥调信息/' % (heap_sn)
    X = api.api_read(host, path)

    if X is None:
        return None

    # 将用户设置值写入数据中心
    for key, value in user_set_dict.items():
        if key not in X:
            continue

        if type(value) == type(''):
            u_value = int(value)
        else:
            u_value = value

        # 值相同则不写入
        if u_value == X[key]:
            continue

        u_path = path + key + '/'
        print(u_path)
        api.api_write(host, u_path, u_value, visitor)

    return True


# 获取PCS遥调
def get_pcs_yaotiao(pcs_sn):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/PCS数据块/%d/PCS遥调信息/' % (pcs_sn)
    X = api.api_read(host, path)

    if X is None:
        return {}

    return X


# 设置PCS遥调
def set_pcs_yaotiao(pcs_sn, user_set_dict, visitor=None):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/PCS数据块/%d/PCS遥调信息/' % (pcs_sn)
    X = api.api_read(host, path)
    yaotiao = {
        "恒功率模式功率_AC": 10,
        "恒功率模式功率_DC": 10,
        "恒压模式限制电流": 10,
        "恒流模式电流": 10,
        "独立逆变频率": 10,
        "功率因数": 10,
        "无功功率": 10,
        "状态标志位": 10,
        "电池充电满恢复值": 10,
        "恒压模式电压": 10,
        "电池充电限制电流": 10,
        "电池放电空值": 10,
        "电池放电空恢复值": 10,
        "无功比例": 10,
        "电池充电满值": 10,
        "电池放电限制电流": 10,
        "独立逆变电压": 10
    }

    if X is None:
        return False

    try:
        # 将用户设置值写入数据中心
        for key, value in user_set_dict.items():
            if key in X:
                if type(value) == type(''):
                    if int(value) == X[key]:
                        continue
                    api.api_write(host, path + key, int(value), visitor)
                else:
                    api.api_write(host, path + key, value, visitor)
        return True
    except Exception as e:
        return False


# 设置PCS遥控
def set_pcs_yaokong(pcs_sn, name, value, visitor=None):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/PCS数据块/%d/PCS遥控信息/%s/' % (pcs_sn, name)
    X = api.api_read(host, path)

    if X is None:
        return None

    return api.api_write(host, path, value, visitor)


# 获取PCS遥控
def get_pcs_yaokong(pcs_sn):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/PCS数据块/%d/PCS遥控信息/' % (pcs_sn)
    X = api.api_read(host, path)

    if X is None:
        return None

    return X


# 获取PCS遥测值
def get_pcs_yaoce(pcs_sn):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/PCS数据块/%d/PCS遥测信息/' % (pcs_sn)
    X = api.api_read(host, path)

    if X is None:
        return None

    return X


# 获取PCS个数
def get_pcs_count():
    try:
        with codecs.open('data/configure/外设数量参数/PCS设备数量.json', encoding='utf8') as file:
            count = json.load(file)
    except Exception as e:
        return 0
    return count


# 获取协议盒遥信信息
def get_sample_yx():
    host = get_datacenter_address()
    path = get_datacenter_root() + '/开关量协议盒数据块/开关量协议盒遥信信息/'
    X = api.api_read(host, path)

    if X is None:
        return None

    return X


# 获取协议盒遥测信息
def get_sample_yc():
    host = get_datacenter_address()
    path = get_datacenter_root() + '/开关量协议盒数据块/开关量协议盒遥测信息/'
    X = api.api_read(host, path)

    if X is None:
        return None

    return X


#获取蜂鸣器遥控
def get_bee_yaokong():
    host = get_datacenter_address()
    path = get_datacenter_root() + '/SCADA/'
    X = api.api_read(host, path)

    if X is None:
        return None

    return X


# 设置蜂鸣器遥控
def set_bee_yaokong(name, value, visitor=None):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/SCADA/%s/' % name
    X = api.api_read(host, path)

    if X is None:
        return None

    return api.api_write(host, path, value, visitor)


# 获取数据中心节点地址
def get_datacenter_address():
    try:
        with codecs.open('data/configure/监控通讯参数/数据中心地址.json', encoding='utf8') as file:
            http_ip = json.load(file)

        with codecs.open('data/configure/监控通讯参数/HTTP协议端口.json', encoding='utf8') as file:
            http_port = json.load(file)
    except Exception as e:
        return '127.0.0.1:8083'

    return '%s:%d' % (http_ip, http_port)


# 获取数据中心的根目录
def get_datacenter_root():
    return "/v1.0/realtime"


# 获取系统中BMS的个数
def get_bms_count():
    try:
        with codecs.open('data/configure/外设数量参数/BMS设备数量.json', encoding='utf8') as file:
            count = json.load(file)
    except Exception as e:
        return 0
    return count


# 获取系统中空调的个数
def get_aircondition_count():
    try:
        with codecs.open('data/configure/外设数量参数/空调设备数量.json', encoding='utf8') as file:
            count = json.load(file)
    except Exception as e:
        return 0
    return count


# 获取指定BMSID的电池组数
def get_bms_group_count(bms_id):
    try:
        with codecs.open('data/configure/BMS参数/%d/BCMU数量-%d.json' % (bms_id, bms_id), encoding='utf8') as file:
            count = json.load(file)
    except Exception as e:
        return 0
    return count


# 获取电池节数
def get_bms_battery_count(bms_id, group_id):
    try:
        with codecs.open('data/configure/BMS参数/%d/电池数量-%d.json' % (bms_id, bms_id), encoding='utf8') as file:
            count = json.load(file)
    except Exception as e:
        return 0
    return count


# 获取PACK内温度采样点个数
def get_temperature_simple_count():
    try:
        with codecs.open('data/configure/电池参数/pack内置温度采样点个数.json', encoding='utf8') as file:
            count = json.load(file)
    except Exception as e:
        return 1
    return count


# 获取历史故障显示方式
def get_history_error_show_method():
    try:
        with codecs.open('data/configure/系统通用参数/历史故障显示方式.json', encoding='utf8') as file:
            method = json.load(file)
    except Exception as e:
        return '列表'

    return method


# 获取历史事件显示方式
def get_history_event_show_method():
    try:
        with codecs.open('data/configure/系统通用参数/历史事件显示方式.json', encoding='utf8') as file:
            method = json.load(file)
    except Exception as e:
        return '列表'

    return method


# 设置BMS日期时间
def sync_bms_datetime(bms_id, dt):
    pass


# 设置PCS日期时间
def sync_pcs_datetime(pcs_id):
    pass


# 设置EMS日期时间
def sync_ems_datetime(ems):
    pass


# 获取版本数据块
def get_version_blank():
    host = get_datacenter_address()
    path = get_datacenter_root() + '/软件版本数据块/'
    X = api.api_read(host, path)
    return X


# 获取全部空调数据
def get_aircondition(aid):
    host = get_datacenter_address()
    path = get_datacenter_root() + '/空调数据块/%d/' % aid
    X = api.api_read(host, path)
    return {} if X is None else X
