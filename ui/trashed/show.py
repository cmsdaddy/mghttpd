from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import os
import time
import csv


# 显示所有的摘要项
def list_all_substract(request, pid):
    return Http404(request)


# 显示所有的图表项
def list_all_grid(request, pid):
    return Http404(request)


# 显示所有的遥测项
def list_all_yaoce(request, pid):
    return Http404(request)


# 显示所有的遥信项
def list_all_yaoxin(request, pid):
    return Http404(request)


def vote_up_element(request, id):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    try:
        ele = Element.objects.get(id=id)
        ele.order -= 1
        ele.save()
    except:
        pass

    try:
        next = request.GET['next']
    except:
        next = '/'

    return HttpResponseRedirect(next)


def vote_down_element(request, id):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    try:
        ele = Element.objects.get(id=id)
        ele.order = ele.order + 1
        ele.save()
    except:
        pass

    try:
        next = request.GET['next']
    except:
        next = '/'

    return HttpResponseRedirect(next)


def delete_element(request, id):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    if request.GET['next']:
        next = request.GET['next']
    else:
        next = '/'

    try:
        obj = Element.objects.get(id=id)
        datapoints = obj.datapoint.all()

        for dp in datapoints:
            dp.refer_count -= 1
            dp.save()

        obj.delete()
    except:
        pass

    return HttpResponseRedirect(next)


# 将上传的文件保存到upload目录，返回保存文件的路径
def save_upload_file(request, filename):
    file = request.FILES.get("csvfile", None)
    if not file:
        return None

    path = 'upload/' + filename
    with open(path, "wb") as upload:
        for chunk in file.chunks():
            upload.write(chunk)

    return path


#
def import_target_is_abstract(pid, datapoint):
    page = Page.objects.get(id=pid)
    el = Element(page=page, type=ElementType.objects.get(type='abstract'),
                 name=datapoint.short_name)
    el.save()
    #el = Element.objects.get(id=el.id)
    el.datapoint.add(datapoint)
    el.save()


def import_target_is_yaoce(pid, datapoint):
    page = Page.objects.get(id=pid)
    el = Element(page=page, type=ElementType.objects.get(type='yaoce'),
                 name=datapoint.short_name)
    el.save()
    #el = Element.objects.get(id=el.id)
    el.datapoint.add(datapoint)
    el.save()


def import_target_is_yaoxin(pid, datapoint):
    page = Page.objects.get(id=pid)
    el = Element(page=page, type=ElementType.objects.get(type='yaoxin'),
                 name=datapoint.short_name)
    el.save()
    #el = Element.objects.get(id=el.id)
    el.datapoint.add(datapoint)
    el.save()


# 向当前页面导入数据点
def import_datapoint(request, pid):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    try:
        target = request.GET['target']
    except Exception as e:
        target = 'abstract'

    if request.method == 'GET':
        context = {
            'pid': pid,
            'action': '/datapoint/import/%d/?target=%s' % (pid, target),
            'title': '导入新的数据点',
            'request': request
        }
        return render(request, 'show/import_遥测_遥信_摘要.html', context=context)
      elif request.method != 'POST':
        return HttpResponseNotAllowed()

    filename = "page-%d-datapoint-%s" % (int(pid), str(time.time()))
    csv_path = save_upload_file(request, filename)
    if csv_path is None:
        return HttpResponseRedirect('/page/%d' % int(pid))

    try:
        with open(csv_path,) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    obj = DataPoint.objects.get(access_path=row['path'])
                except Exception as e:
                    obj = DataPoint(
                        short_name = row['shortname'],
                        datatype = DataPointType.objects.get(name=row['type']),
                        access_path=row['path'],
                        k = float(row['k']),
                        b = float(row['b']),
                        mask = int(row['mask'], 16),
                        dot = int(row['dot']),
                        unit= row['unit'],
                        max_record = int(row['records']),
                    )
                obj.save()

                if target == 'abstract':
                    obj.refer_count += 1
                    import_target_is_abstract(pid, obj)
                elif target == 'yaoce':
                    obj.refer_count += 1
                    import_target_is_yaoce(pid, obj)
                elif target == 'yaoxin':
                    obj.refer_count += 1
                    import_target_is_yaoxin(pid, obj)

                obj.save()

    except Exception as e:
        print(e)
        return HttpResponseServerError()

    return HttpResponseRedirect('/page/%d' % pid)
