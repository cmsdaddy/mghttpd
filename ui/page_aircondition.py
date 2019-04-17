import os
import random
import time
import datetime
from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *

import ui.page_history as history
import ui.mg as mg
import ui.page_report as report


def show_all_list(request):
    context = dict()
    air_list = list()

    air_count = mg.get_aircondition_count()
    context['air_list'] = air_list

    for aid in range(air_count):
        pack = mg.get_aircondition(aid)
        air = dict(**pack)
        air['id'] = aid + 1
        air_list.append(air)

    return render(request, "03-空调设备管理/空调列表.html", context=context)


def show_aircondition(request, aid):
    context = dict()
    air_list = list()

    pack = mg.get_aircondition(aid)
    air = dict(**pack)
    air['id'] = aid + 1
    context['air'] = air

    return render(request, "03-空调设备管理/空调详细数据.html", context=context)
