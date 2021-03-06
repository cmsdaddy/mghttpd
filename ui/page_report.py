from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import os
import datetime
# from datetime import datetime
import ui.mg as mg
import random
import ui.api as api
import ui.systerecords as sysrecords
import xlwt
from io import BytesIO
from django.utils import timezone
from glob import glob


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

    return render(request, "01-BMS设备管理/堆报表-24小时.html", context=context)


# 输出一周内的报告
# def report_heap_week(request, heap_id, ctx):
#     records_list = list()
#     context = dict(**ctx)
#     context['records_list'] = records_list
#     weekname = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期天']
#
#     objs = BMSYaoce.objects.filter(bmsid=heap_id).all()
#     x_now = datetime.datetime.now()
#     now = datetime.datetime(year=x_now.year, month=x_now.month, day=x_now.day,
#                             hour=x_now.hour, minute=0, second=0, microsecond=0)
#     begin = now - datetime.timedelta(days=7)
#
#     days = list()
#     charged = list()
#     discharged = list()
#
#     for t in range(7):
#         #report = select_datetime_range_report(heap_id, begin)
#         end = datetime.timedelta(days=1) + begin
#         records = BMSYaoce.objects.filter(tsp__gte=begin, tsp__lt=end)
#
#         # ======================================
#         x = [record.total_charged_kwh for record in records]
#         try:
#             charged.append(max(x) - min(x))
#         except:
#             charged.append(0)
#
#         # ======================================
#         x = [record.total_discharged_kwh for record in records]
#         try:
#             discharged.append(max(x) - min(x))
#         except:
#             discharged.append(0)
#
#         days.append(weekname[begin.weekday()] + "\n%02d-%02d" % (begin.month, begin.day))
#         begin += datetime.timedelta(days=1)
#
#     context['days'] = days
#     context['charged_kwh'] = [random.randrange(10, 100) for _ in range(7)]
#     context['discharged_kwh'] = [random.randrange(10, 100) for _ in range(7)]
#     return render(request, "bms/堆报表-本周.html", context=context)


# 输出一个月内的报告
# def report_heap_month(request, heap_id, ctx):
#     records_list = list()
#     context = dict(**ctx)
#     context['records_list'] = records_list
#
#     x_now = datetime.datetime.now()
#     now = datetime.datetime(year=x_now.year, month=x_now.month, day=x_now.day,
#                             hour=x_now.hour, minute=0, second=0, microsecond=0)
#     begin = now - datetime.timedelta(months=1)
#
#     days = list()
#     charged = list()
#     discharged = list()
#
#     for t in range(30):
#         end = datetime.timedelta(days=1 + begin)
#         records = BMSYaoce.objects.filter(tsp__gte=begin, tsp__lt=end)
#
#         x = [record.total_charged_kwh for record in records]
#         try:
#             charged.append(max(x) - min(x))
#         except:
#             charged.append(0)
#
#         x = [record.total_discharged_kwh for record in records]
#         try:
#             discharged.append(max(x) - min(x))
#         except:
#             discharged.append(0)
#
#         begin += datetime.timedelta(days=1)
#
#
#     return render(request, "bms/堆报表-本月.html", context=context)

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
    # 检测所有驱动器
    usb_state = 0
    # sdb_devices = map(os.path.realpath, glob('sys/block/sd*'))
    sdb_devices = map(os.path.realpath, glob("/sys/block/*"))
    for dev in list(sdb_devices):
        if 'usb' in dev.split('/')[5]:
            usb_state = 1
            print('发现U盘')
            break
        else:
            usb_state = 0
            print('未发现U盘')
            continue
    context['usb_state'] = usb_state
    print(usb_state)
    return render(request, "96-系统报表管理/系统报表管理.html", context=context)


#报表导出
def system_report_export(request,start_times,end_times):
    excel_name = str(datetime.datetime.now().date()) + 'report.xls'
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # response['Content-Disposition'] = 'attachment;filename=BMS.xls'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(excel_name)
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
    sheet.write(0, 2, '总充电电量/kwh', style_heading)
    sheet.write(0, 3, '总放电电量/kwh', style_heading)
    sheet.write(0, 4, '最高电池电压/V', style_heading)
    sheet.write(0, 5, '最低电池电压/V', style_heading)
    sheet.write(0, 6, '充电次数(总计)', style_heading)
    sheet.write(0, 7, '放电次数(总计)', style_heading)

    data_row = 1
    current_list = list()
    #格式化时间
    start_times = datetime.datetime.strptime(start_times,'%Y-%m-%d')
    end_times = datetime.datetime.strptime(end_times,'%Y-%m-%d')
    start_times = datetime.datetime(year=start_times.year,month=start_times.month,day=start_times.day)
    end_times = datetime.datetime(year=end_times.year,month=end_times.month,day=end_times.day)
    for i in BMSYaoce.objects.all():
        if i.tsp > start_times and i.tsp < end_times:
            sheet.write(data_row, 0, i.bmsid)
            sheet.write(data_row, 1, str(i.tsp))
            sheet.write(data_row, 2, i.total_charged_kwh)
            sheet.write(data_row, 3, i.total_discharged_kwh)
            sheet.write(data_row, 4, '%.3f'%(i.bat_max_voltage/1000.0))
            sheet.write(data_row, 5, '%.3f'%(i.bat_min_voltage/1000.0))
        else:
            pass

        data_row += 1

        current_list.append(i.current)

    #计算充放电次数
    count_charge = 0
    count_discharge = 0
    for j in current_list:
        if j > 0 and current_list[current_list.index(j) + 1] > 0 and current_list[current_list.index(j) + 2] < 0:
            count_charge += 1
        else:
            pass

        if j < 0 and current_list[current_list.index(j) + 1] < 0 and current_list[current_list.index(j) + 2] > 0:
            count_discharge += 1
        else:
            pass

    sheet.write(1, 6, count_charge)
    sheet.write(1, 7, count_discharge)

    #写出到IO
    output = BytesIO()
    wb.save(output)
    usbpath = '/home/cyf/Desktop/test/' + excel_name

    output.seek(0)
    response.write(output.getvalue())
    save(wb.save(output), usbpath)
    return response

def save(html, path):
    '''
    以文件形式保存数据
    :param html: 要保存的数据
    :param path: 保存路路径
    :return: 
    '''
    if not os.path.exists(os.path.split(path)[0]):
        os.makedirs(os.path.split(path)[0])

    try:
        #保存数据到文件
        with open(path,'w') as f:
            f.write(str(html))
        print('success')

    except Exception as e:
        print('fail',e)