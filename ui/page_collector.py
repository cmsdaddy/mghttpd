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


# 记录数据
def data_record(request, cid):
    print(request.POST)
    try:
        collector = Collector.objects.get(id=cid)
    except:
        return HttpResponse('{"status":"fail", "data": %d}' % cid)

    tsp = request.POST['tsp']
    data = request.POST['data']

    record = DataPointRecords(collector=collector, datetime=tsp, record=data)
    record.save()

    return HttpResponse('{"status":"ok", "data": %d}' % cid)


# 创建一个采集器ID，若已经存在则返回ID
def create_collector(request):
    print(request.POST)
    try:
        #obj = json.loads(request.body.decode('utf8'))
        path = request.POST['path']
    except Exception as e:
        print(e)
        return HttpResponse('{"status":"fail"}')

    try:
        collector = Collector.objects.get(path=path)
    except:
        collector = Collector(path=path)
        collector.save()

    return HttpResponse('{"status":"ok", "data": %d}' % collector.id)
