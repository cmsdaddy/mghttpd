# -*- coding: utf8 -*-
from django.urls import path
from django.http import *
from django.shortcuts import render
import os
import re


def get_login_on_display_list():
    """返回系统当前登录到界面上的所有用户列表"""
    login_list = list()
    try:
        with os.popen(r'who | grep -e "(:[0-9]\+)"') as pipe:
            while True:
                line = pipe.readline()
                if not line or len(line) == 0:
                    break
                p = r'(?P<username>\S+)\s+(?P<tty>tty\d+)\s+(?P<login>\d{4}(-\d{2}){2} [^\s]+)\s\((?P<display>:\d+)\)'
                r = re.match(p, line)
                login = r.groupdict()
                admin = {'is_superuser': True}
                user = {'is_superuser': False}

                if login['username'] in {'admin', 'administrator'}:
                    login = dict(login, **admin)
                else:
                    login = dict(login, **user)
                login_list.append(login)
    except Exception as e:
        print(e)
    return login_list


def do_linux_logout(request):
    """退出当前登录用户，若有多个弹出选择框"""
    login_list = get_login_on_display_list()

    if request.method == 'POST':
        login = dict(request.POST)
    elif len(login_list) == 1:
        login = login_list[0]
    else:
        login = None

    if login:
        os.system('(sleep 2;pkill -t {})&'.format(login['tty']))
        return render(request, "linux/logout-splash.html", context={'login': login})
    else:
        return render(request, "linux/logout-select.html", context={'login_list': login_list})


def do_linux_reboot(request):
    context = dict()
    os.system("reboot")
    return render(request, "linux/reboot-splash.html", context=context)


def do_linux_halt(request):
    context = dict()
    os.system("halt")
    return render(request, "linux/halt-splash.html", context=context)


def show_linux_control_panel(request):
    context = dict()
    context['cancel'] = request.GET['cancel']
    return render(request, "linux/退出系统选择页面.html", context=context)


urlpatterns = [
    path("", show_linux_control_panel),
    path('logout/', do_linux_logout),
    path('change_user/', do_linux_logout),
    path('reboot/', do_linux_reboot),
    path('halt/', do_linux_halt),
]


urls = (urlpatterns, "linux", "linux")
