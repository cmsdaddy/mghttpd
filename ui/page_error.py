import os
import random
import time
from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *

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
