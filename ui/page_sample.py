from django.shortcuts import render
from django.http import *
from django.urls import path
import ui.mg as mg


def show_location_info(request):
    context = {}
    context['request'] = request

    temp = mg.get_sample_yx()
    context['sample'] = temp

    if temp is None:
        # 避免出现无法引用字段的错误
        temp = dict()

    for state in temp:
        if temp[state] is 0:
            temp[state] = 'OFF'
        elif temp[state] is 1:
            temp[state] = 'ON'

    return render(request, '04-采样设备管理/03-位置量采样信息.html', context=context)


def show_analog_info(request):
    context = {}
    context['request'] = request
    context['sample'] = mg.get_sample_yc()

    return render(request, '04-采样设备管理/02-模拟量采样信息.html', context=context)


def show_simple_main_page(request):
    return render(request, "04-采样设备管理/01-采样显示iframe框架.html")


urlpatterns = [
    path('', show_simple_main_page),
    path('location/', show_location_info),
    path('analog/', show_analog_info),
]
urls = (urlpatterns, 'sample', 'sample')
