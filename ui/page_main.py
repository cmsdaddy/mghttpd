from django.shortcuts import render
from django.urls import path
from django.http import *
from ui.models import *
from django.db.models import *
import os
import ui.mg as mg
import random
import ui.api as api
import ui.systerecords as sysrecords
import socket
import ui.scada as scada

if scada.system_name == 'windows':
    pass
else:
    import fcntl

import struct


# 显示首页
def index(request):
    return render(request, "06-SCADA设备/00-StartUp页面.html")


def show_scada_main(request):
    context = {}

    context['request'] = request
    context['bms_count'] = mg.get_bms_count()
    context['bms_id_list'] = [x for x in range(mg.get_bms_count())]
    context['pcs_count'] = mg.get_pcs_count()
    context["pcs_id_list"] = [x for x in range(mg.get_pcs_count())]

    return render(request, "06-SCADA设备/首页模板.html", context=context)


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if scada.system_name == 'windows':
        return 'n/a'
    else:
        inet_address = fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )
        return socket.inet_ntoa(inet_address[20:24])


def version(request):
    context = dict()
    ifaces_list = list()

    for if_idx, if_name in socket.if_nameindex():
        try:
            ip = get_ip_address(if_name.encode())
        except:
            ip = 'N/A'

        ifaces_list.append((if_name, ip))

    context['ifaces_list'] = ifaces_list

    with os.popen('/bin/ip address') as pipe:
        context['ifaces_more_information'] = pipe.read()

    version_blank = mg.get_version_blank()
    context['version'] = version_blank
    context['request'] = request
    try:
        context['next'] = request.GET['next']
    except Exception as e:
        context['next'] = '/'

    return render(request, "06-SCADA设备/00-SCADA程序版本信息.html", context=context)


urlpatterns = [
    path('', index),
    path('main/', show_scada_main, name="scada_main_url"),
    path('version/', version),

    path('logout/', lambda request: HttpResponseRedirect('/linux/logout/')),
    path('change_user/', lambda request: HttpResponseRedirect('/linux/change_user/')),
    path('reboot/', lambda request: HttpResponseRedirect('/linux/reboot/')),
    path('halt/', lambda request: HttpResponseRedirect('/linux/halt/')),
]
urls = (urlpatterns, 'main', 'main')