from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import os
import json
import time
from django.utils import timezone


# 显示数据采集器列表
def list_all_collector(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    collectors = Collector.objects.all()

    context = {
        'request': request,
        'total': Collector.objects.count(),
        'collectors': collectors,
    }

    return render(request, "collector/list_数据采集器.html", context=context)


# 添加一个数据采集器
def new_collector(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    if request.method == 'GET':
        context = {
            'request': request,
            'action': '/collector/new/',
            'submit': '创建',
            'collector': Collector()
        }
        return render(request, "collector/edit_数据采集器.html", context=context)
    elif request.method != 'POST':
        return render(request, "error/notimplement.html", {'request': request})

    d = Collector.objects.aggregate(Max('id'))
    id = 1
    if d['id__max'] is None:
        id = 1
    else:
        id = d['id__max'] + 1

    # post
    collector = Collector()
    collector.id = id
    collector.name = request.POST['name']
    collector.period = int(request.POST['period'])
    collector.protocol = request.POST['protocol']
    collector.host = request.POST['host']
    collector.apipaths = request.POST['apipaths']
    collector.type = request.POST['type']
    collector.operator = request.POST['operator']
    collector.maxcount = int(request.POST['maxcount'])
    if collector.record == False:
        collector.maxcount = 1

    if request.POST['record'] == 'on':
        collector.record = True
    else:
        collector.record = False

    if request.POST['disabled'] == 'off':
        collector.disabled = True
    else:
        collector.disabled = False

    collector.save()

    return HttpResponseRedirect("/collector/?from=" + request.path)


# 编辑数据采集器
def edit_collector(request, cid):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    try:
        collector = Collector.objects.get(id=cid)
    except Exception as e:
        return Http404()

    if request.method == 'GET':
        context = {
            'request': request,
            'action': '/collector/%d/' % collector.id,
            'submit': '修改',
            'collector': collector
        }
        return render(request, "collector/edit_数据采集器.html", context=context)
    elif request.method != 'POST':
        return render(request, "error/notimplement.html", {'request': request})

    collector.name = request.POST['name']
    collector.period = int(request.POST['period'])
    collector.protocol = request.POST['protocol']
    collector.host = request.POST['host']
    collector.apipaths = request.POST['apipaths']
    collector.type = request.POST['type']
    collector.operator = request.POST['operator']
    collector.maxcount = int(request.POST['maxcount'])

    if request.POST['record'] == 'on':
        collector.record = True
    else:
        collector.record = False
        collector.maxcount = 1

    if request.POST['disabled'] == 'off':
        collector.disabled = True
    else:
        collector.disabled = False

    collector.save()
    return HttpResponseRedirect("/collector/?from=" + request.path)


# 改变采集器工作状态
def collector_disabled_toggle(request, cid):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    try:
        collector = Collector.objects.get(id=cid)
    except Exception as e:
        return Http404()

    if request.method == 'GET':
        if collector.disabled == False:
            collector.disabled = True
        else:
            collector.disabled = False

    collector.save()
    return HttpResponseRedirect("/collector/?from=" + request.path)


# 删除数据采集器
def delete_collector(request, cid):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    try:
        collector = Collector.objects.get(id=cid)
    except Exception as e:
        return Http404()

    collector.delete()
    return HttpResponseRedirect("/collector/?from=" + request.path)


# 返回数据采集器的JSON数据
def output_collector_as_json(request):
    datapoints = DataPoint.objects.filter(refer_count__gt=0)
    dp_list = []
    for dp in datapoints:
        obj = {'id': dp.id, 'access_path': dp.access_path, 'ref': dp.refer_count,
               'k': dp.k, 'b': dp.b, 'mask': dp.mask, 'dot': dp.dot}
        dp_list.append(obj)
    return HttpResponse(json.dumps(dp_list))


# 记录采集器数据
def record_collector_data(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    data = request.POST['data']
    print(data)
    jobj = json.loads(data)

    datetime = jobj['tsp']
    datapoints_json = jobj['data']
    count = 0
    for did, value in datapoints_json:
        dp = DataPoint.objects.get(id=did)
        if dp.max_record <= 1:
            DataPointRecords.objects.filter(datapoint=dp).all().delete()
        dpr = DataPointRecords(datapoint=dp, datetime=datetime, record=value)
        dpr.save()
        count += 1

    return HttpResponse('{"status": "ok", "count": %d}' % count)


def list_collecor_data(request, cid):
    """列出指定个数的数据"""
    try:
        collector = Collector.objects.get(id=cid)
    except:
        return Http404()

    count = 1
    begin = None

    try:
        count = int(request.GET['count'])
    except:
        count = 1

    try:
        begin = int(request.GET['begin'])
    except:
        begin = None

    if collector.record is False:
        count = 1

    if begin is None:
        records = CollectorRecord.objects.filter(collector=cid).order_by('-datatime')[: count]
    else:
        records = CollectorRecord.objects.filter(collector=cid).order_by('-datatime')[begin: count]

    record_list = []
    for record in records:
        #print(record.id, record.datatime, record.data)
        record_list.append(record.data)

    respons = HttpResponse('{"status":"ok", "data":[' + ",".join(record_list) + "]}")
    respons['Content-Type'] = 'application/json'
    return respons


def bind_grid_with_collector(request, gid):
    """将数据源绑定至制定图表上"""
    try:
        grid = Grid.objects.get(id=gid)
    except:
        return HttpResponseBadRequest()

    try:
        collector_count = Collector.objects.count()
        collector_list = Collector.objects.filter(disabled=False)
    except:
        return HttpResponseBadRequest()

    if request.method == 'GET':
        try:
            config = json.loads(grid.datasource)
            cid = config['datasource']
        except:
            cid = -1

        context = {
            "request": request,
            "grid": grid,
            "cid": cid,
            "collector_count": collector_count,
            "collector_list": collector_list,
        }
        return render(request, "collector/bind_数据采集器.html", context=context)

    if request.method != 'POST':
        return HttpResponseBadRequest()

    try:
        cid = int(request.POST['collector'])
    except:
        return HttpResponseBadRequest()

    if cid == -1:
        grid.datasource = '{}'
        grid.save()
    else:
        j = request.POST['json']
        obj = json.loads(j)
        obj['datasource'] = cid
        grid.datasource = json.dumps(obj, indent=4)
        grid.save()

    return HttpResponseRedirect("/collector/")
