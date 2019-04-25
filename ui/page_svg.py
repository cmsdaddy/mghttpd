# -*- coding: utf8 -*-
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


def svg_learn_test(request):
    return render(request, "92-SVG测试/01-测试.html")


urlpatterns = [
    path('', svg_learn_test, name="svg url"),
]
urls = (urlpatterns, 'main', 'main')
