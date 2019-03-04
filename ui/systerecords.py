# -*- coding: utf8 -*-
from __future__ import print_function
from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import os
import ui.mg as mg
import random
import ui.api as api


sysrecords = {
    "系统安装时间": "",
    "系统首次启动时间": "",
    "前一次启动时间": "",
    "前一次关闭时间": "",
}


def system_startup():
    global sysrecords
