import os
import random
import time
from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
from django.urls import path
from django.http import *

import ui.page_history as history
import ui.mg as mg


def noerror(request):
    context = dict()
    context['request'] = request

    return render(request, "error/form-操作等待模板.html", context=context)


def form_commit_success(request):
    context = dict()
    context['request'] = request
    try:
        context['code'] = request.GET['code']
    except:
        context['code'] = 0

    try:
        context['next'] = request.GET['next']
    except:
        context['next'] = '/'

    return render(request, "error/form-提交成功模板.html", context=context)


def form_commit_fail(request):
    context = dict()
    context['request'] = request

    try:
        context['code'] = request.GET['code']
    except:
        context['code'] = 0

    try:
        context['next'] = request.GET['next']
    except:
        context['next'] = '/'

    return render(request, "error/form-提交错误模板.html", context=context)


def disk_space_low(request):
    context = dict()
    with os.popen("df -h|grep sd[a-z][0-9]") as pipe:
        context['df_information'] = pipe.read()

    with os.popen("du -hd1 /") as pipe:
        context['du_root_information'] = pipe.read()

    return render(request, "error/warning-磁盘空间不足警告.html", context=context)


def system_emergency(request):
    return disk_space_low(request)


def backup_and_cleanup(request):
    context = dict()
    return render(request, "error/notimplement.html", context=context)


url_patterns = [
    path("noerror/", noerror),
    path("formok/", form_commit_success),
    path("formerror/", form_commit_fail),
    path("emergency/", system_emergency),
    path("backup_and_cleanup/", backup_and_cleanup)
]


urls = (url_patterns, "error", "error")