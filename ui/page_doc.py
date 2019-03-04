from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import os
import ui.mg as mg
import random
import ui.api as api
import time
import ui.page_history as history
import json
import os
import sys


def show_index(request):
    context = dict()
    context['request'] = request
    return render(request, "doc/index.html", context=context)
