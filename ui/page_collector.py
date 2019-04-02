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


def show_general_collector_profile_page(request):
    context = dict()
    context['const_env_list'] = {
        "PROJECT_NAME": '"1',
        "TIMESTAMP_FORMAT": '%Y-%m-%d %H:%M%:S.%f',
    }
    return render(request, "collector/index.html", context=context)


collector_url_map = [
    path('', show_general_collector_profile_page),
]
urls = (collector_url_map, 'collector', 'collector')
