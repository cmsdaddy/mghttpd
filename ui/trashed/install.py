from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import os
import json
import time
from django.utils import timezone
import ui.install_datapoints as InstallDataPoint
import ui.install_elements as InstallElement


# 清空系统中全部数据
def on_reset_all(request):
    print(">>>>开始清理系统数据<<<<<")

    print("  >>> 显示元素记录: %d 条" % Element.objects.count())
    elements_all = Element.objects.all()
    for ele in elements_all:
        ele.datapoint.all().delete()
    elements_all.delete()

    print("  >>> 页面数据: %d 条" % Page.objects.count())
    Page.objects.all().delete()

    print("  >>> 历史数据记录: %d 条" % DataPointRecords.objects.count())
    DataPointRecords.objects.all().delete()

    print("  >>> 数据点记录: %d 条" % DataPoint.objects.count())
    DataPoint.objects.all().delete()

    print("  >>> 数据点类型记录: %d 条" % DataPointType.objects.count())
    DataPointType.objects.all().delete()

    print("  >>> 显示元素类型记录: %d 条" % ElementType.objects.count())
    ElementType.objects.all().delete()

    return HttpResponseRedirect("/install/")


def on_install_command(request):
    # yaoce-遥测 yaoxin-遥信 abstract-摘要 gridx12-图表x12 gridx8-图表x8 gridx6-图表x6 gridx4-图表x4
    elementtypes = [
        ('yaoce','遥测'),
        ('yaoxin', '遥信'),
        ('abstract', '摘要'),
        ('gridx12' ,'图表x12'),
        ('gridx8', '图表x8'),
        ('gridx6', '图表x6'),
        ('gridx4', '图表x4'),
    ]

    for type, name in elementtypes:
        try:
            et = ElementType.objects.get(type=type)
        except Exception as e:
            et = ElementType(name=name, type=type)
            et.save()
            print("install %s<--->%s @ElementType" % (type, name))

    DataPointTypeMaps = [
        ('string', '字符串'),
        ('number', '数字'),
        ('object', '对象'),
        ('object-array', '对象数组'),
        ('number-arrary', '数字数组'),
        ('string-array', '字符串数组'),
    ]
    # 安装数据点类型
    for type, name in DataPointTypeMaps:
        try:
            dt = DataPointType.objects.get(type=type)
        except Exception as e:
            dt = DataPointType(name=name, type=type)
            dt.save()
            print("install %s<--->%s @DataPointType" % (type, name))

    page_count = Page.objects.count()
    if page_count == 0:
        page_count = install_default_page()

    print("共计安装页面 %d 个" % page_count)
    return HttpResponseRedirect("/")


# 安装默认页面
def install_default_page():
    # 首页
    title = "微电网系统-首页"
    name = "首页"
    print("install %s @Page" % title)
    page = Page(title=title, name=name, template="首页模板.html", display_order=-9000)
    page.save()

    display_order = 1
    # 电池堆最多16组
    for heap_sn in range(0, 1):
        display_order = install_battery_heap(heap_sn, display_order, True)

        # 每个堆支持16组电池
        for group_sn in range(0, 4):
            display_order = install_battery_group(heap_sn, group_sn, display_order, True)

    # PCS页面
    title = "微电网系统-PCS页面"
    name = "储能PCS"
    print("install %s @Page" % title)
    page = Page(title=title, name=name, template="PCS模板.html", display_order=display_order, display=False)
    page.save()

    # 光伏页面
    # 风电页面
    # EMS页面

    return display_order


# 安装电池堆页面
def install_battery_heap(heap_sn, begin_display_order, display):
    title = "微电网系统-%d#电池堆" % (heap_sn + 1)
    name = "%d#堆" % (heap_sn + 1)
    print("install %s @Page" % title)
    page = Page(title=title, name=name, devicesn=heap_sn, template="蓄电池模板_堆信息.html", display_order=begin_display_order, display=display)
    page.save()
    begin_display_order += 1

    count = InstallDataPoint.install_battery_heap_datapoints(page, heap_sn)
    print("install %d points @电池堆 DataPoint" % count)

    return begin_display_order


# 安装电池组页面
def install_battery_group(heap_sn, group_sn, begin_display_order, display):
    # 电池组信息
    title = "微电网系统-%d#电池组" % (group_sn + 1)
    name = "%d堆-%d#电池组" % (heap_sn + 1, group_sn + 1)
    page = Page(title=title, name=name, devicesn=group_sn, template="蓄电池模板_组信息.html", display_order=begin_display_order, display=display)
    page.save()
    begin_display_order += 1

    count = InstallDataPoint.install_battery_group_main_datapoints(page, heap_sn, group_sn)
    print("install %d points @电池组-摘要 DataPoint" % count)

    # 电池组遥调页面
    title = "微电网系统-%d#电池组-遥调页面" % (group_sn + 1)
    name = "%d堆-%d#电池组-遥调页面" % (heap_sn + 1, group_sn + 1)
    page = Page(title=title, name=name, devicesn=group_sn, template="蓄电池模板_遥调.html", display_order=begin_display_order, display=display)
    page.save()
    begin_display_order += 1

    count = InstallDataPoint.install_battery_group_yaotiao_datapoints(page, heap_sn, group_sn)
    print("install %d points @电池组-遥调 DataPoint" % count)

    # 电池组单体电压页面
    title = "微电网系统-%d#电池组-单体电压" % (group_sn + 1)
    name = "%d堆-%d#电池组-单体电压" % (heap_sn + 1, group_sn + 1)
    page_V = Page(title=title, name=name, devicesn=group_sn, template="蓄电池模板_单体电压.html", display_order=begin_display_order, display=display)
    page_V.save()
    begin_display_order += 1

    # 电池组单体温度页面
    title = "微电网系统-%d#电池组-单体温度" % (group_sn + 1)
    name = "%d堆-%d#电池组-单体温度" % (heap_sn + 1, group_sn + 1)
    page_T = Page(title=title, name=name, devicesn=group_sn, template="蓄电池模板_单体温度.html", display_order=begin_display_order, display=display)
    page_T.save()
    begin_display_order += 1

    # 电池组单体SOC页面
    title = "微电网系统-%d#电池组-单体SOC" % (group_sn + 1)
    name = "%d堆-%d#电池组-单体SOC" % (heap_sn + 1, group_sn + 1)
    page_SOC = Page(title=title, name=name, devicesn=group_sn, template="蓄电池模板_单体SOC.html", display_order=begin_display_order, display=display)
    page_SOC.save()
    begin_display_order += 1

    # 电池组单体SOH页面
    title = "微电网系统-%d#电池组-单体SOH" % (group_sn + 1)
    name = "%d堆-%d#电池组-单体SOH" % (heap_sn + 1, group_sn + 1)
    page_SOH = Page(title=title, name=name, devicesn=group_sn, template="蓄电池模板_单体SOH.html", display_order=begin_display_order, display=display)
    page_SOH.save()
    begin_display_order += 1

    count = InstallDataPoint.install_battery_group_danti_datapoints(page_V, page_T, page_SOC, page_SOH, heap_sn, group_sn)
    print("install %d points @电池组-单体信息 DataPoint" % count)

    return begin_display_order

