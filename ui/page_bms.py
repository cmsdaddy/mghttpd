import os
import random
import time
import datetime
from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *

import ui.page_history as history
import ui.mg as mg
import ui.page_report as report
from django.urls import path
import ui.cache as cache
import math


# 默认显示单体信息时的列数
__default_display_single_battery_column_count = 20


# 返回单体信息显示的标题列数据
def get_single_battery_table_title_row(comumn_count):
    x = ['#']
    x.extend([str(x) for x in range(1, comumn_count + 1)])
    return x


# 获取单体电压数组
def __get_single_battery_V(heap_sn, group_sn, battery_count):
    return ["%.3f" % (random.random() + 3)] * battery_count


# 获取单体温度
def __get_single_battery_T(heap_sn, group_sn, battery_count):
    return ["%d" % random.randrange(25, 30)] * battery_count


# 获取单体SOC
def __get_single_battery_SOC(heap_sn, group_sn, battery_count):
    return ["%d" % random.randrange(90, 100)] * battery_count


# 获取单体SOH
def __get_single_battery_SOH(heap_sn, group_sn, battery_count):
    return ["%d" % random.randrange(98, 100)] * battery_count


# 获取单体信息显示数据数组
def __make_single_battery_table(X, battery_count, column_count):
    row_data = []
    f, t = 0, column_count
    bcount = 0

    while bcount <= battery_count:
        if f >= battery_count:
            break

        row = X[f: t]
        row_data.append(row)

        f += column_count
        if t + column_count > battery_count:
            t = battery_count + 1
        else:
            t += column_count

        bcount += column_count

    return row_data


# 获取单体电压行数据
def get_single_battery_V_rows(heap_sn, group_sn, battery_count, column_count):
    X = mg.get_single_battery_V(heap_sn, group_sn, battery_count)
    battery_cache = cache.BatterySingleVoltageCache()
    battery_cache.set(heap_sn, group_sn, X)
    return __make_single_battery_table(X, battery_count, column_count)


# 获取单体温度行数据
def get_single_battery_T_rows(heap_sn, group_sn, battery_count, column_count):
    X = mg.get_single_battery_T(heap_sn, group_sn, battery_count)
    return __make_single_battery_table(X, battery_count, column_count)


# 获取单体SOC行数据
def get_single_battery_SOC_rows(heap_sn, group_sn, battery_count, column_count):
    X = mg.get_single_battery_SOC(heap_sn, group_sn, battery_count)
    return __make_single_battery_table(X, battery_count, column_count)


# 获取单体SOH行数据
def get_single_battery_SOH_rows(heap_sn, group_sn, battery_count, column_count):
    X = mg.get_single_battery_SOH(heap_sn, group_sn, battery_count)
    return __make_single_battery_table(X, battery_count, column_count)


# 显示电池堆信息
def show_bms_heap(request, bms_sn):
    bms_heap = mg.get_bms_heap_yaoce(bms_sn)
    bms = dict(bms_heap)
    try:
        bms['电池堆电流'] = bms['电池堆电流'] / 100.0
        bms['电池堆电压'] = bms['电池堆电压'] / 100.0
        bms['电池堆SOC'] = bms['电池堆SOC'] / 100.0
    except:
        pass

    context = {
        "request": request,
        "bms_id": bms_sn,
        "type": "heap",
        "bms_name": "%d#电池堆" % (bms_sn + 1),
        "group_id_list": [x for x in range(mg.get_bms_group_count(bms_sn))],
        "bms_origin": bms_heap,
        "bms": bms,
    }

    try:
        report_range = request.GET['range']
    except KeyError:
        report_range = 'live'

    if report_range == 'day':
        return report.report_heap_day(request, bms_sn, context)
    elif report_range == 'week':
        return report.report_heap_week(request, bms_sn, context)
    # elif report_range == 'month':
    #     return report.report_heap_month(request, bms_sn, context)
    else:
        pass

    return render(request, "bms/堆.html", context=context)


def get_hours_record(collector, limit_hours):
    records = DataPointRecords.objects.filter(collector=collector, datetime__gt=limit_hours)
    l = list()
    pre = None
    for r in records:
        if pre is None:
            pre = r
            l.append(r)
            continue
        if pre.record == r.record:
            continue

        pre = r
        l.append(r)
    return l


def show_bms_group_grid(request, bms_sn, group_sn):
    bms_heap = mg.get_bms_heap_yaoce(bms_sn)
    context = {
        "request": request,
        "bms_id": bms_sn,
        "group_id": group_sn,
        "type": "group_grid",
        "bms_name": "%d#电池堆" % (bms_sn + 1),
        "group_id_list": [ x for x in range(mg.get_bms_group_count(bms_sn))],
        "bms_origin": bms_heap,
        "bms": dict(bms_heap),
    }
    try:
        befor = 0 - int(request.GET['befor'])
    except:
        befor = -48

    now = datetime.datetime.now()
    before_hours = now + datetime.timedelta(hours=befor)

    V = []
    I = []
    SOC = []

    # 获取当前BMS遥测值
    now_yaoce = mg.get_bms_heap_yaoce(bms_sn)

    # 获取24小时范围内的全部BMS记录
    records = BMSGroupYaoce.objects.filter(bmsid=bms_sn, bmsgid=group_sn, tsp__gte=before_hours, tsp__lt=now)

    soc_pre = 0
    V_pre = 0
    I_pre = 0
    for record in records:
        if record.SOC == soc_pre:
            pass
        else:
            SOC.append({"datetime": record.tsp, "record": record.SOC})
            soc_pre = record.SOC

        # 5V 的变化幅度才记录
        if abs(record.voltage - V_pre) < 500:
            pass
        else:
            V.append({"datetime": record.tsp, "record": record.voltage})
            V_pre = record.voltage

        if record.current == I_pre:
            pass
        else:
            I.append({"datetime": record.tsp, "record": record.current})
            I_pre = record.current

    context['SOC'] = SOC
    context['V'] = V
    context['I'] = I

    return render(request, "bms/组-曲线图.html", context=context)


def show_bms_grid(request, bms_sn):
    #bms_heap = mg.get_bms_heap_yaoce(bms_sn)
    context = {
        "request": request,
        "bms_id": bms_sn,
        "type": "heap-grid",
        "bms_name": "%d#电池堆" % (bms_sn + 1),
        "group_id_list": [ x for x in range(mg.get_bms_group_count(bms_sn))],
    #    "bms_origin": bms_heap,
    #    "bms": dict(bms_heap),
    }

    """
    try:
        befor = 0 - int(request.GET['befor'])
    except:
        befor = -48

    now = datetime.datetime.now()
    before_hours = now + datetime.timedelta(hours=befor)

    V = []
    I = []
    SOC = []

    # 获取当前BMS遥测值
    # now_yaoce = mg.get_bms_heap_yaoce(bms_sn)

    # 获取24小时范围内的全部BMS记录
    records = BMSYaoce.objects.filter(bmsid=bms_sn, tsp__gte=before_hours, tsp__lt=now)
    soc_pre = 0
    V_pre = 0

    I_pre = 0
    for record in records:
        if record.SOC == soc_pre:
            pass
        else:
            SOC.append({"datetime": record.tsp, "record": record.SOC})
            soc_pre = record.SOC

        # 5V 的变化幅度才记录
        if abs(record.voltage - V_pre) < 500:
            pass
        else:

            V.append({"datetime": record.tsp, "record": record.voltage})
            V_pre = record.voltage

        if record.current == I_pre:
            pass
        else:
            I.append({"datetime": record.tsp, "record": record.current})
            I_pre = record.current

    context['SOC'] = SOC
    context['V'] = V
    context['I'] = I
    """

    return render(request, "bms/堆-曲线图.html", context=context)


def makeup_bms_grid(request, bms_sn):
    pass


yaotiao_black_list = {"状态标志位"}
# 显示电池堆遥调
def show_bms_heap_yaotiao(request, bms_sn):
    if request.method == 'POST':
        X = {key: value for key, value in request.POST.items()}
        if "时间" in X:
            x = request.POST['时间']
            t = [int(x[0:4], 10), int(x[4: 6], 10), int(x[6: 8], 10),
                                  int(x[8: 10], 10), int(x[10: 12], 10), int(x[12: 14], 10)]
            X['时间'] = t

        success = mg.set_bms_heap_yaotiao(bms_sn, X, str(request.user))
    else:
        success = True

    yaotiao = mg.get_bms_yaotiao(bms_sn)
    yaotiao_list = mg.filter_api_yaotiao(yaotiao, blacklist=yaotiao_black_list, column=3)

    context = {
        "request": request,
        "success": success,
        "bms_id": bms_sn,
        "type": "heap-yaotiao",
        "bms_name": "%d#电池堆" % (bms_sn + 1),
        "group_id_list": [ x for x in range(mg.get_bms_group_count(bms_sn))],
        "yaotiao_list": yaotiao_list,
    }

    return render(request, "bms/堆-遥调.html", context=context)


# 显示电池组信息
def show_bms_group(request, bms_sn, group_sn):
    bms_yaoce = mg.get_bms_group_yaoce(bms_sn, group_sn)

    context = {
        "request": request,
        "bms_id": bms_sn,
        "type": "group",
        "group_id": group_sn,
        "battery_count": mg.get_bms_battery_count(bms_sn, group_sn),
        "bms_name": "%d#电池堆" % (bms_sn + 1),

        "group_V": bms_yaoce['组端电压'],
        "group_I": bms_yaoce['组端电流'],
        "group_SOC": bms_yaoce['组SOC'],
        "group_SOH": bms_yaoce['组SOH'],
        "group_charge_count": bms_yaoce['充电次数'],
        "group_discharge_count": bms_yaoce['放电次数'],
        "group_available_cap": bms_yaoce['可用能量'],
        "group_charge_cap": bms_yaoce['累计充电容量'],
        "group_discharge_cap": bms_yaoce['累计放电容量'],
        "group_average_T": bms_yaoce['平均温度'],
        "group_average_V": bms_yaoce['平均电压'],
        "group_V_max": bms_yaoce['最高单体电压'],
        "group_V_min": bms_yaoce['最低单体电压'],
        "group_T_max": bms_yaoce['单体最高温度'],
        "group_T_min": bms_yaoce['单体最低温度'],
        "group_SOC_max": bms_yaoce['单体SOC最大值'],
        "group_SOC_min": bms_yaoce['单体SOC最小值'],
        "group_SOH_max": bms_yaoce['单体SOH最大值'],
        "group_SOH_min": bms_yaoce['单体SOH最小值'],
        "bms_yaoce": bms_yaoce,
    }

    return render(request, "bms/组.html", context=context)


# 显示电池组单体电压
def show_bms_group_V(request, bms_sn, group_sn):
    try:
        battery_count = int(request.GET['count'])
    except:
        battery_count = mg.get_bms_battery_count(bms_sn, group_sn)

    try:
        column_count = int(request.GET['column'])
    except:
        column_count = __default_display_single_battery_column_count

    try:
        period = int(request.GET['period'])
    except:
        period = 15

    title_row = get_single_battery_table_title_row(column_count)
    data_rows = get_single_battery_V_rows(bms_sn, group_sn, battery_count-1, column_count)

    rows = list()
    for row in data_rows:
        rows.extend(row)

    part1, part2, part3, part4 = rows[:50], rows[50:100], rows[100:150], rows[150:]
    user_define_data_rows = [part1]
    if len(part2) > 0:
        user_define_data_rows.append(part2)
    if len(part3) > 0:
        user_define_data_rows.append(part3)
    if len(part4) > 0:
        user_define_data_rows.append(part4)

    equal_voltage = round(sum(rows)/len(rows), 3)
    standard_deviation = sum([pow(v - equal_voltage, 2) for v in rows ]) / len(rows)
    variance = math.sqrt(standard_deviation)

    context = {
        "request": request,
        "bms_id": bms_sn,
        "type": "group_V",
        "group_id": group_sn,
        "period": period,
        "col_count": column_count,
        "title_row": title_row,
        "data_rows": data_rows,
        "column_count": column_count,
        "battery_count": battery_count,
        "bms_name": "%d#电池堆" % (bms_sn + 1),
        "user_define_data_rows": user_define_data_rows,
        "equal_voltage": equal_voltage,
        "max_voltage": max(rows),
        "min_voltage": min(rows),
        "max_sub_min": round(max(rows) - min(rows), 3),
        "standard_deviation": round(standard_deviation, 3),
        "variance": round(variance, 3),
    }

    try:
        style = request.GET['style']
    except:
        return render(request, "bms/组-单体电压-line.html", context=context)

    if style == 'line':
        return render(request, "bms/组-单体电压-line.html", context=context)
    elif style == 'bar':
        return render(request, "bms/组-单体电压-bar.html", context=context)
    else:
        return render(request, "bms/组-单体电压.html", context=context)


# 显示电池组单体温度
def show_bms_group_T(request, bms_sn, group_sn):
    try:
        battery_count = int(request.GET['count'])
    except:
        battery_count = mg.get_bms_battery_count(bms_sn, group_sn)

    try:
        column_count = int(request.GET['column'])
    except:
        column_count = __default_display_single_battery_column_count

    try:
        period = int(request.GET['period'])
    except:
        period = 15

    title_row = get_single_battery_table_title_row(column_count)
    data_rows = get_single_battery_T_rows(bms_sn, group_sn, int((int((battery_count)-1)) / mg.get_temperature_simple_count()), column_count)

    context = {
        "request": request,
        "bms_id": bms_sn,
        "type": "group_T",
        "group_id": group_sn,
        "period": period,
        "title_row": title_row,
        "data_rows": data_rows,
        "column_count": column_count,
        "battery_count": mg.get_bms_battery_count(bms_sn, group_sn),
        "bms_name": "%d#电池堆" % (bms_sn + 1),
    }

    return render(request, "bms/组-单体温度.html", context=context)


# 显示电池组单体SOC
def show_bms_group_SOC(request, bms_sn, group_sn):
    try:
        battery_count = int(request.GET['count'])
    except:
        battery_count = mg.get_bms_battery_count(bms_sn, group_sn)

    try:
        column_count = int(request.GET['column'])
    except:
        column_count = __default_display_single_battery_column_count

    try:
        period = int(request.GET['period'])
    except:
        period = 15

    title_row = get_single_battery_table_title_row(column_count)
    data_rows = get_single_battery_SOC_rows(bms_sn, group_sn, battery_count-1, column_count)

    context = {
        "request": request,
        "bms_id": bms_sn,
        "type": "group_SOC",
        "group_id": group_sn,
        "period": period,
        "title_row": title_row,
        "data_rows": data_rows,
        "column_count": column_count,
        "battery_count": mg.get_bms_battery_count(bms_sn, group_sn),
        "bms_name": "%d#电池堆" % (bms_sn + 1),
    }

    return render(request, "bms/组-单体SOC.html", context=context)


# 显示电池组单体SOH
def show_bms_group_SOH(request, bms_sn, group_sn):
    try:
        battery_count = int(request.GET['count'])
    except:
        battery_count = mg.get_bms_battery_count(bms_sn, group_sn)

    try:
        column_count = int(request.GET['column'])
    except:
        column_count = __default_display_single_battery_column_count

    try:
        period = int(request.GET['period'])
    except:
        period = 15

    title_row = get_single_battery_table_title_row(column_count)
    data_rows = get_single_battery_SOH_rows(bms_sn, group_sn, battery_count-1, column_count)

    context = {
        "request": request,
        "bms_id": bms_sn,
        "type": "group_SOH",
        "group_id": group_sn,
        "period": period,
        "title_row": title_row,
        "data_rows": data_rows,
        "column_count": column_count,
        "battery_count": mg.get_bms_battery_count(bms_sn, group_sn),
        "bms_name": "%d#电池堆" % (bms_sn + 1),
    }

    return render(request, "bms/组-单体SOH.html", context=context)


# 显示电池组遥测
def show_bms_group_yaoce(request, bms_sn, group_sn):
    context = {
        "request": request,
        "bms_id": bms_sn,
        "type": "group_yaoce",
        "group_id": group_sn,
        "battery_count": mg.get_bms_battery_count(bms_sn, group_sn),
        "bms_name": "%d#电池堆" % (bms_sn + 1),
    }

    return render(request, "bms/组-遥测.html", context=context)


# 显示电池组遥信
def show_bms_group_yaoxin(request, bms_sn, group_sn):
    context = {
        "request": request,
        "bms_id": bms_sn,
        "type": "group_yaoxin",
        "group_id": group_sn,
        "events_count": 21,
        "yaoxin_event_list": [{"datetime": "2018-03-02 23:33:12", "content": "电池1SOC过高"}] * 20,
        "battery_count": mg.get_bms_battery_count(bms_sn, group_sn),
        "bms_name": "%d#电池堆" % (bms_sn + 1),
    }

    return render(request, "bms/组-遥信.html", context=context)


grid_url_map = [
    path('', lambda request: HttpResponseRedirect(request.path + "0/")),
    path('<int:bms_sn>/', show_bms_heap),
    path('<int:bms_sn>/yaotiao/', show_bms_heap_yaotiao),
    path('<int:bms_sn>/grid/', show_bms_grid),
    path('<int:bms_sn>/grid/makeup', makeup_bms_grid),
    path('<int:bms_sn>/group/', lambda request: HttpResponseRedirect(request.path + "0/")),
    path('<int:bms_sn>/group/<int:group_sn>/', show_bms_group),
    path('<int:bms_sn>/group/<int:group_sn>/grid/', show_bms_group_grid),
    path('<int:bms_sn>/group/<int:group_sn>/V/', show_bms_group_V),
    path('<int:bms_sn>/group/<int:group_sn>/T/', show_bms_group_T),
    path('<int:bms_sn>/group/<int:group_sn>/SOC/', show_bms_group_SOC),
    path('<int:bms_sn>/group/<int:group_sn>/SOH/', show_bms_group_SOH),
    path('<int:bms_sn>/group/<int:group_sn>/yaoce/', show_bms_group_yaoce),
    path('<int:bms_sn>/group/<int:group_sn>/yaoxin/', show_bms_group_yaoxin),
]
urls = (grid_url_map, 'bms', 'bms')
