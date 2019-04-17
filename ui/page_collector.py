import os
import random
import time
import json
from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import ui.page_history as history
import ui.mg as mg
from django.urls import path
from django.shortcuts import render
from django.http import *
import ui.scada as scada
import codecs


profile_path = scada.profile_dir_path + '/collector.json'


def read_collector_profile_without_error():
    try:
        with codecs.open(profile_path, encoding='utf8') as file:
            profile = json.loads(file.read(), encoding='utf8')
    except:
        profile = dict()

    return profile


def write_collector_profile_without_error(new_profile):
    try:
        with codecs.open(profile_path, encoding='utf8') as file:
            profile = json.loads(file.read(), encoding='utf8')
    except:
        profile = dict()

    profile = dict(profile, **new_profile)

    with codecs.open(profile_path, mode='w', encoding='utf8') as file:
        json.dump(profile, file, ensure_ascii=False, indent=2)

    return profile


def show_general_collector_profile_page(request):
    if request.method == 'GET':
        profile = read_collector_profile_without_error()
        return render(request, "93-采集器控制管理/01-采集器基本信息.html", context=profile)

    profile = {key: values[0] for key, values in dict(request.POST).items()}
    write_collector_profile_without_error(profile)
    return HttpResponseRedirect(request.path)


def show_collector_env_page(request):
    context = dict()
    context['const_env_list'] = {
        "PROJECT_NAME": '"1',
        "TIMESTAMP_FORMAT": '%Y-%m-%d %H:%M%:S.%f',
    }
    return render(request, "93-采集器控制管理/06-采集器环境变量.html", context=context)


def show_collector_yaoce_page(request):
    context = dict()
    #return render(request, "93-采集器控制管理/04-采集器遥测采集控制.html", context=context)
    return render(request, "93-采集器控制管理/07-采集单元提交表单.html", context=context)


def show_collector_yaoxin_page(request):
    context = dict()
    return render(request, "93-采集器控制管理/02-采集器遥信采集控制.html", context=context)


def show_collector_yaokong_page(request):
    context = dict()
    return render(request, "93-采集器控制管理/03-采集器遥控采集控制.html", context=context)


def show_collector_yaotiao_page(request):
    context = dict()
    return render(request, "93-采集器控制管理/05-采集器遥调采集控制.html", context=context)


collector_url_map = [
    path('', show_general_collector_profile_page),
    path('env/', show_collector_env_page),
    path('yaoce/', show_collector_yaoce_page),
    path('yaoxin/', show_collector_yaoxin_page),
    path('yaokong/', show_collector_yaokong_page),
    path('yaotiao/', show_collector_yaotiao_page),
]
urls = (collector_url_map, 'collector', 'collector')
