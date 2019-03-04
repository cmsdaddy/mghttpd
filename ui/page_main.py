from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import os
import ui.mg as mg
import random
import ui.api as api
import ui.systerecords as sysrecords


# 显示首页
def index(request):
    context = {}

    context['request'] = request
    context['bms_count'] = mg.get_bms_count()
    context['bms_id_list'] = [x for x in range(mg.get_bms_count())]
    context['pcs_count'] = mg.get_pcs_count()
    context["pcs_id_list"] = [x for x in range(mg.get_pcs_count())]

    return render(request, "首页模板.html", context=context)


def version(request):
    context = dict()
    version_blank = mg.get_version_blank()
    context['version'] = version_blank
    context['request'] = request
    try:
        context['next'] = request.GET['next']
    except Exception as e:
        context['next'] = '/'

    return render(request, "version.html", context=context)


def show_logout_page(request):
    context = dict()

    context['request'] = request
    try:
        context['cancel'] = request.GET['cancel']
    except:
        context['cancel'] = '/'

    return render(request, "退出系统选择页面.html", context=context)

def show_login_page(request):
    context = dict()
    return render(request,'admin.html',context=context)

def show_change_page(request):
    # (sleep 2;pkill -t tty7) &
    os.system('(sleep 2;pkill -t tty7)&')
    # print("kill tty7")
    return HttpResponseRedirect('/admin/logout?next=/')
