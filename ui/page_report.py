from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import os
import datetime
import ui.mg as mg
import random
import ui.api as api
import ui.systerecords as sysrecords
import xlwt
from io import BytesIO


def select_datetime_range_report(bmsid, begin):
    end = datetime.timedelta(hours=1) + begin
    records = BMSYaoce.objects.filter(tsp__gte=begin, tsp__lt=end)
    print(begin, end, records.count())
    record = dict()

    x = [record.bmsid for record in records]
    x = [record.tsp for record in records]

    # ======================================
    x = [record.bat_gid_of_min_temp for record in records]
    try:
        record['最低单体温度_组编号'] = x[0]
    except:
        record['最低单体温度_组编号'] = None

    # ======================================
    x = [record.bat_gid_of_max_temp for record in records]
    try:
        record['最高单体温度_组编号'] = x[0]
    except:
        record['最高单体温度_组编号'] = None

    # ======================================
    x = [record.bat_gid_of_min_voltage for record in records]
    try:
        record['最低单体电压_组编号'] = x[0]
    except:
        record['最低单体电压_组编号'] = None

    # ======================================
    x = [record.bat_gid_of_max_voltage for record in records]
    try:
        record['最高单体电压_组编号'] = x[0]
    except:
        record['最高单体电压_组编号'] = None

    # ======================================
    x = [record.bat_min_temp for record in records]
    try:
        record['最低单体温度_值'] = x[0]
    except:
        record['最低单体温度_值'] = None

    # ======================================
    x = [record.bat_max_temp for record in records]
    try:
        record['最高单体温度_值'] = x[0]
    except:
        record['最高单体温度_值'] = None

    # ======================================
    x = [record.bat_min_voltage for record in records]
    try:
        record['最低单体电压_值'] = x[0]
    except:
        record['最低单体电压_值'] = None

    # ======================================
    x = [record.bat_max_voltage for record in records]
    try:
        record['最高单体电压_值'] = x[0]
    except:
        record['最高单体电压_值'] = None

    # ======================================
    x = [record.SOC for record in records]
    try:
        record['堆SOC_最大值'] = max(x)
    except:
        record['堆SOC_最大值'] = None

    try:
        record['堆SOC_最小值'] = min(x)
    except:
        record['堆SOC_最小值'] = None

    x = [record.chargable_kwh for record in records]
    x = [record.dischargable_kwh for record in records]
    x = [record.status for record in records]

    # ======================================
    x = [record.voltage for record in records]
    try:
        record['堆电压_最大值'] = max(x)
    except:
        record['堆电压_最大值'] = None

    try:
        record['堆电压_最小值'] = min(x)
    except:
        record['堆电压_最小值'] = None

    # ======================================
    x = [record.current for record in records]
    try:
        record['堆电流_最大值'] = max(x)
    except:
        record['堆电流_最大值'] = None

    try:
        record['堆电流_最小值'] = min(x)
    except:
        record['堆电流_最小值'] = None

    # ======================================
    x = [record.total_charged_kwh for record in records]
    try:
        record['充电量'] = max(x) - min(x)
    except:
        record['充电量'] = None

    # ======================================
    x = [record.total_discharged_kwh for record in records]
    try:
        record['放电量'] = max(x) - min(x)
    except:
        record['放电量'] = None

    return record


# 输出一天内的报告
def report_heap_day(request, heap_id, ctx):
    records_list = list()
    context = dict(**ctx)
    context['records_list'] = records_list

    objs = BMSYaoce.objects.filter(bmsid=heap_id).all()
    x_now = datetime.datetime.now()
    now = datetime.datetime(year=x_now.year, month=x_now.month, day=x_now.day,
                            hour=x_now.hour, minute=0, second=0, microsecond=0)
    begin = now - datetime.timedelta(hours=24)
    for t in range(24):
        report = select_datetime_range_report(heap_id, begin)
        record = {'time_range': "%02d:00~%02d:59" % (begin.hour, begin.hour) }
        begin += datetime.timedelta(hours=1)

        record = dict(record, **report)
        records_list.append(record)

    return render(request, "bms/堆报表-24小时.html", context=context)


# 输出一周内的报告
def report_heap_week(request, heap_id, ctx):
    records_list = list()
    context = dict(**ctx)
    context['records_list'] = records_list
    weekname = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期天']

    objs = BMSYaoce.objects.filter(bmsid=heap_id).all()
    x_now = datetime.datetime.now()
    now = datetime.datetime(year=x_now.year, month=x_now.month, day=x_now.day,
                            hour=x_now.hour, minute=0, second=0, microsecond=0)
    begin = now - datetime.timedelta(days=7)

    days = list()
    charged = list()
    discharged = list()

    for t in range(7):
        #report = select_datetime_range_report(heap_id, begin)
        end = datetime.timedelta(days=1) + begin
        records = BMSYaoce.objects.filter(tsp__gte=begin, tsp__lt=end)

        # ======================================
        x = [record.total_charged_kwh for record in records]
        try:
            charged.append(max(x) - min(x))
        except:
            charged.append(0)

        # ======================================
        x = [record.total_discharged_kwh for record in records]
        try:
            discharged.append(max(x) - min(x))
        except:
            discharged.append(0)

        days.append(weekname[begin.weekday()] + "\n%02d-%02d" % (begin.month, begin.day))
        begin += datetime.timedelta(days=1)

    context['days'] = days
    context['charged_kwh'] = [random.randrange(10, 100) for _ in range(7)]
    context['discharged_kwh'] = [random.randrange(10, 100) for _ in range(7)]
    return render(request, "bms/堆报表-本周.html", context=context)


# 输出一个月内的报告
def report_heap_month(request, heap_id, ctx):
    records_list = list()
    context = dict(**ctx)
    context['records_list'] = records_list

    x_now = datetime.datetime.now()
    now = datetime.datetime(year=x_now.year, month=x_now.month, day=x_now.day,
                            hour=x_now.hour, minute=0, second=0, microsecond=0)
    begin = now - datetime.timedelta(months=1)

    days = list()
    charged = list()
    discharged = list()

    for t in range(30):
        end = datetime.timedelta(days=1 + begin)
        records = BMSYaoce.objects.filter(tsp__gte=begin, tsp__lt=end)

        x = [record.total_charged_kwh for record in records]
        try:
            charged.append(max(x) - min(x))
        except:
            charged.append(0)

        x = [record.total_discharged_kwh for record in records]
        try:
            discharged.append(max(x) - min(x))
        except:
            discharged.append(0)

        begin += datetime.timedelta(days=1)


    return render(request, "bms/堆报表-本月.html", context=context)

#系统报表
def show_system_report(request):
    context = dict()

    # context['request'] = request
    # context['bms_count'] = mg.get_bms_count()
    # context['bms_id_list'] = [x for x in range(mg.get_bms_count())]
    # context['pcs_count'] = mg.get_pcs_count()
    # context["pcs_id_list"] = [x for x in range(mg.get_pcs_count())]
    #
    #
    # context['errors_total_count'] = HistoryError.objects.filter(elevel__lte=2).count()
    #
    # # 系统投运时间
    # first_start = HistoryError.objects.filter(abstrct="系统启动").order_by('etsp_begin')[0]
    # now = datetime.datetime.now()
    # days = (now - first_start.etsp_begin).days
    # context['rolling_days'] = 1 if days == 0 else days
    #
    # # 系统启动时间
    # startup = HistoryError.objects.filter(abstrct="系统启动").order_by('-etsp_begin')[0]
    # now = datetime.datetime.now()
    # delta = now - startup.etsp_begin
    #
    # running_total = list()
    # if delta.days > 0:
    #     running_total.append("%d天" % delta.days)
    # if len(running_total) == 0:
    #     running_total.append("不足1天")
    #
    # context['running_days'] = "".join(running_total)
    # context['startup_tsp'] = startup.etsp_begin

    return render(request, "系统报表.html", context=context)

#报表导出
def system_report_export(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=BMS报表.excel'

    wb = xlwt.Workbook(encoding='utf8')
    sheet = wb.add_sheet('BMS报表-sheet')

    style_heading = xlwt.easyxf("""
            font:
                name Arial,
                bold on,
                height 0xA0;
            align:
                wrap off,
                vert center,
                horiz center;
            pattern:
                pattern solid;
            borders:
                left THIN,
                right THIN,
                top THIN,
                bottom THIN;
            """)

    sheet.write(0, 0, 'bmsid', style_heading)
    sheet.write(0, 1, '时间', style_heading)
    sheet.write(0, 2, '充电次数', style_heading)
    sheet.write(0, 3, '放电次数', style_heading)
    sheet.write(0, 4, '总充电电量', style_heading)
    sheet.write(0, 5, '总放电电量', style_heading)
    sheet.write(0, 6, '最高电池电压', style_heading)
    sheet.write(0, 7, '最低电池电压', style_heading)

    data_row = 1
    for i in BMSYaoce.objects.all():
        # tsp_time = i.tsp.strftime('%Y-%M-%D-%H-%M-%S')
        sheet.write(data_row, 0, i.bmsid)
        sheet.write(data_row, 1, i.tsp)
        sheet.write(data_row, 2, i.bmsid)
        sheet.write(data_row, 3, i.bmsid)
        sheet.write(data_row, 4, i.total_charged_kwh)
        sheet.write(data_row, 5, i.total_discharged_kwh)
        sheet.write(data_row, 6, i.bat_max_voltage)
        sheet.write(data_row, 7, i.bat_min_voltage)

        data_row += 1

    #写出到IO
    output = BytesIO()
    wb.save(output)

    output.seek(0)
    response.write(output.getvalue())

    return response
