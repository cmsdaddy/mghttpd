# -*- coding: utf8 -*-
import os
import random
import json
import time
import codecs
from django.shortcuts import render
from django.http import *
from django.urls import path
import datetime
import ui.scada as scada


def show_log_main_page(request):
    context = dict()

    log_files = list()
    try:
        for log in os.listdir(scada.log_dir_path):
            log_files.append('/'.join([scada.log_dir_path, log]))

    except FileNotFoundError:
        os.mkdir(scada.log_dir_path, mode=0o777)

    context['log_files'] = log_files
    return render(request, "07-系统日志管理/01-日志查看面板.html", context=context)


def show_text_file(request):
    try:
        full_path = request.GET['file']
    except:
        return HttpResponseRedirect("/log/help/")

    def read_file_iter(path):
        with codecs.open(path, encoding='utf8') as file:
            while True:
                line = file.readline()
                if line:
                    yield line
                else:
                    raise StopIteration

    context = dict()
    context['txt_file_generator'] = read_file_iter(full_path)
    return render(request, "07-系统日志管理/03-日志显示页面.html", context=context)


def show_help_page(request):
    return render(request, "07-系统日志管理/02-日志帮助页面.html")


urlpatterns = [
    path('', show_log_main_page),
    path('read/', show_text_file),
    path('help/', show_help_page),
]


urls = (urlpatterns, "log", "log")