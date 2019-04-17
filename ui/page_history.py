from django.shortcuts import render
from django.http import *
from django.urls import path
from ui.models import *
from django.db.models import *
import os
import ui.mg as mg
import random
import ui.api as api
from ui import page
import time
import json


# 导出全部历史记录数据
def export_history(request):
    pass


def parser_multipage_parameters(request, default_show_count=None, default_show_page=None):
    '''
    解析URL的显示参数, 根据URL参数返回显示的页码和每页显示的个数
    '''
    if default_show_count is None:
        default_show_count = 20
    if default_show_page is None:
        default_show_page = 0

    try:
        show_count = int(request.GET['count'])
    except:
        show_count = default_show_count

    try:
        show_page = int(request.GET['page'])
    except:
        show_page = default_show_page

    return show_count, show_page


def calc_show_paramters(method, show_count, records_count):
    if method == '鱼骨图' and show_count >= 5 and records_count >= 5:
        show_count = 5
    else:
        method = '列表'

    return show_count, method


# 显示当前故障/事件信息列表
def show_current_all_errors(request):
    try:
        show_count, show_page = parser_multipage_parameters(request)
        records = CurrentError.objects.all()
        context = page.multipage_processor(records, show_page, show_count)
        return render(request, "05-系统历史事件管理/当前故障列表.html", context=context)
    except Exception as e:
        return HttpResponse('{"status": "fail"}')


# 显示历史故障/事件信息列表
def show_history_all_errors(request):
    try:
        show_count, show_page = parser_multipage_parameters(request)
        records = HistoryError.objects.filter(elevel__lte=2)
        context = page.multipage_processor(records, show_page, show_count)
        return render(request, "05-系统历史事件管理/历史故障列表.html", context=context)
    except Exception as e:
        print(e)
        return HttpResponse('{"status": "fail"}')


def show_history_error_detail(request):
    """显示历史数据的详细信息"""
    context = dict()
    ueid = request.GET['ueid']
    context['record'] = HistoryError.objects.get(ueid=ueid)
    return render(request, "05-系统历史事件管理/历史故障详情.html", context=context)


def show_history_error_confirm(request):
    """显示历史数据的确认页面"""
    pass


def show_history_all_records(request):
    """显示全部历史记录"""
    try:
        show_count, show_page = parser_multipage_parameters(request)
        records = HistoryError.objects.all()
        context = page.multipage_processor(records, show_page, show_count)
        return render(request, "05-系统历史事件管理/历史故障列表.html", context=context)
    except Exception as e:
        print(e)
        return HttpResponse('{"status": "fail"}')


def show_history_all_events(request):
    """显示全部历史事件"""
    try:
        show_count, show_page = parser_multipage_parameters(request)
        records = HistoryError.objects.filter(elevel__gt=2)
        method = mg.get_history_event_show_method()
        show_count, method = calc_show_paramters(method, show_count, records.count())

        context = page.multipage_processor(records, show_page, show_count)
        template = "history/历史故障列表.html" if method == '列表' else "history/历史故障列表-时间轴图.html"
        return render(request, template, context=context)
    except Exception as e:
        print(e)
        return HttpResponse('{"status": "fail"}')


def show_history_all_yaokong_events(request):
    """显示全部遥控历史事件"""
    try:
        show_count, show_page = parser_multipage_parameters(request)
        records = HistoryError.objects.filter(eclass__contains='遥控')
        method = mg.get_history_event_show_method()
        show_count, method = calc_show_paramters(method, show_count, records.count())

        context = page.multipage_processor(records, show_page, show_count)
        template = "history/历史故障列表.html" if method == '列表' else "history/历史故障列表-时间轴图.html"
        return render(request, template, context=context)
    except Exception as e:
        print(e)
        return HttpResponse('{"status": "fail"}')


def show_history_all_yaotiao_events(request):
    """显示全部遥调历史事件"""
    try:
        show_count, show_page = parser_multipage_parameters(request)
        records = HistoryError.objects.filter(eclass__contains='遥调')
        method = mg.get_history_event_show_method()
        show_count, method = calc_show_paramters(method, show_count, records.count())

        context = page.multipage_processor(records, show_page, show_count)
        template = "history/历史故障列表.html" if method == '列表' else "history/历史故障列表-时间轴图.html"
        return render(request, template, context=context)
    except Exception as e:
        print(e)
        return HttpResponse('{"status": "fail"}')


def show_history_error_test(request):
    """显示全部遥调历史事件"""
    try:
        show_count, show_page = parser_multipage_parameters(request)
        records = HistoryError.objects.all()
        context = page.multipage_processor(records, show_page, show_count)
        return render(request, "05-系统历史事件管理/历史故障列表-时间轴图.html", context=context)
    except Exception as e:
        print(e)
        return HttpResponse('{"status": "fail"}')


urlpatterns = [
    # 全部历史记录
    path('all/', show_history_all_records),
    # 当前故障
    path('', show_current_all_errors),
    # 当前故障
    path('current/all/', show_current_all_errors),
    # 全部历史故障
    path('errors/all/', show_history_all_errors),
    # 全部历史事件
    path('events/all/', show_history_all_events),
    # 全部遥控历史事件
    path('events/yaokong/all/', show_history_all_yaokong_events),
    # 全部遥调历史事件
    path('events/yaotiao/all/', show_history_all_yaotiao_events),

    path('show/', show_history_error_detail),
    path('confirm/', show_history_error_confirm),

    path('test/', show_history_error_test),

    path('export/', export_history),
]

urls = (urlpatterns, "history", "history")