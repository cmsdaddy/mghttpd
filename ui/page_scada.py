# -*- coding: utf8 -*-
import os
import random
import json
import time
from django.shortcuts import render
from django.http import *
from django.urls import path
from ui.models import *
from django.db.models import *
import ui.mg as mg
import ui.page_history as history
import datetime
import ui.page_grid as grid


def show_alarm_control_page(request):
    context = dict()

    if len(request.GET) >= 1:
        for key, value in request.GET.items():
            if key == '蜂鸣器遥控点':
                success = mg.set_bee_yaokong(key, int(value), str(request.user))
                context['success'] = success
                break

    try:
        yaokong = mg.get_bee_yaokong()
        for name in yaokong:
            if name == '蜂鸣器遥控点':
                if yaokong[name] == 0:
                    context['beep'] = 0
                elif yaokong[name] == 1:
                    context['beep'] = 1
    except:
        yaokong = {'蜂鸣器遥控点': 0}
        for name in yaokong:
            if name == '蜂鸣器遥控点':
                if yaokong[name] == 0:
                    context['beep'] = 0
                elif yaokong[name] == 1:
                    context['beep'] = 1

    return render(request, "06-SCADA设备/01-全局状态及控制.html", context=context)


url_patterns = [
    # 蜂鸣器状态展示
    path('', lambda request: show_alarm_control_page(request)),
    path('beep/control/', lambda request: show_alarm_control_page(request)),
]


urls = (url_patterns, "scada", "scada")
