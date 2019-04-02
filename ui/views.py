from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import os
import time


def page_not_implemented(request, *c, **any):
    context = {
        'request': request
    }
    return render(request, 'error/notimplement.html', context)


def get_templates_list():
    return os.listdir('templates/display')


# 显示第一个页面
def show_first_page(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    pages = Page.objects.filter(display=True).order_by('display_order')
    if len(pages) == 0:
        context = {
            'request': request,
        }
        return render(request, 'error/novalidpage.html', context)

    page = pages[0]
    context = {
        'request': request,
        'pid': page.id,
        'page': page,
        'pages': pages,
    }
    return render(request, '首页模板.html', context)


def select_leatest_record(datapoint):
    dp = DataPointRecords.objects.filter(datapoint=datapoint).last()
    try:
        return {'value': dp.record, 'datetime': str(dp.datetime), 'unit': datapoint.unit}
    except:
        return {'value': '0', 'datetime': '', 'unit': datapoint.unit}


def select_datapoint_record(datapoint, count):
    if count == 1:
        return select_leatest_record(datapoint)

    dpr = {'value': [], 'datetime': [], 'unit': datapoint.unit, 'name': datapoint.short_name}

    dprs = DataPointRecords.objects.filter(datapoint=datapoint).order_by('-datetime')[:count]
    for dp in dprs:
        dpr['value'].append(float(dp.record))
        dpr['datetime'].append(str(dp.datetime)[6:16])

    dpr['value'].reverse()
    dpr['datetime'].reverse()

    return dpr


# 页面元素缓存，加快渲染，避免频繁操作数据库进行数据筛选
page_elements_cache = {}


# 从数据库中筛选出指定页面的全部内容
def select_show_common_elements_in_page(request, pid, _type):
    try:
        elements_list = []
        try:
            if request.user.is_superuser:
                raise ValueError
            elements = page_elements_cache['page_element_%d_%s' % (pid, _type)]
        except:
            if type(_type) == type(''):
                elements = Element.objects.filter(page=pid, display=True, type=ElementType.objects.get(type=_type)).order_by('order')
            elif type(_type) == type([]):
                elements = Element.objects.filter(page=pid, display=True, type__in=_type).order_by('order')
            else:
                elements = []
            page_elements_cache['page_element_%d' % pid] = elements

        for ele in elements:
            try:
                if request.user.is_superuser:
                    raise ValueError
                datapoints = page_elements_cache['element_points_%d' % ele.id]
            except:
                datapoints = ele.datapoint.all()
                page_elements_cache['element_points_%d' % ele.id] = datapoints

            element = {'id': ele.id, 'type': ele.type, 'name': ele.name, 'count': ele.count}

            records = []
            for datapoint in datapoints:
                try:
                    record = select_datapoint_record(datapoint, ele.count)
                    records.append(record)
                except Exception as e:
                    print(e)

            if len(records) == 1:
                element = dict(element, **records[0])
            else:
                element['records'] = records
                element['datetime'] = records[0]['datetime']

            elements_list.append(element)
    except Exception as e:
        print(e)
        elements_list = []

    return elements_list


# 默认内容
def show_page(request, pid):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    try:
        if request.user.is_superuser:
            raise ValueError
        page = page_elements_cache['page_%d' % pid]
    except:
        page = Page.objects.get(id=pid)

    template_path = "".join(['templates/display/', page.template])
    if os.path.isfile(template_path) is False:
        context = {
            'request': request,
            'page': page,
        }
        return render(request, "error/template_not_found.html", context)

    try:
        if request.user.is_superuser:
            raise ValueError
        grid_types = page_elements_cache['grid_types']
    except:
        grid_types = [
             ElementType.objects.get(type='gridx12'),
             ElementType.objects.get(type='gridx8'),
             ElementType.objects.get(type='gridx6'),
             ElementType.objects.get(type='gridx4'),
        ]
        page_elements_cache['grid_types'] = grid_types

    try:
        if request.user.is_superuser:
            raise ValueError
        pages = page_elements_cache['display_pages']
    except:
        pages = Page.objects.filter(display=True).order_by('display_order')

    context = {
        'request': request,
        'templates': get_templates_list(),
        'pid': pid,
        'page': page,
        'pages': pages,
        'abstract_list': select_show_common_elements_in_page(request, pid, "abstract"),
        'grid_list': select_show_common_elements_in_page(request, pid, grid_types),
        'yaoce_list': select_show_common_elements_in_page(request, pid, "yaoce"),
        'yaoxin_list': select_show_common_elements_in_page(request, pid, "yaoxin"),
    }
    return render(request, 'display/' + page.template, context)


def show_settings(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    context = {
        'request': request
    }
    return render(request, 'settings.html', context)


# 列出页面列表
def list_pages(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    context = {
        'request': request,
        'title': '页面列表',
        'total': Page.objects.count(),
        'pages': Page.objects.all().order_by('display_order'),
    }

    return render(request, "editor/list_pages.html", context)


# 创建新的页面
def new_page(request):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    if request.method == 'POST':
        try:
            title = request.POST['title']
            name = request.POST['name']
            devicesn = int(request.POST['devicesn'])
            template = request.POST['template']
            jsfiles = request.POST['jsfiles']
            cssfiles = request.POST['cssfiles']
            try:
                if request.POST['display'] == 'on':
                    display = True
                else:
                    display = False
            except:
                display = False
            display_order = int(request.POST['display_order'])
            json = request.POST['json']
            page = Page(title=title, name=name, devicesn=devicesn, template=template,
                        jsfiles=jsfiles, cssfiles=cssfiles,
                        display=display, display_order=display_order, json=json)

            d = Page.objects.aggregate(Max('id'))
            if d['id__max'] is None:
                page.id = 1
            else:
                page.id = d['id__max'] + 1

            page.save()
        except Exception as e:
            print(e)

        return HttpResponseRedirect('/editor/page/')

    context = {
        'request': request,
        'pagetitle': '新页面',
        'templates': get_templates_list(),
        'page': Page(title="新页面标题", name="新页面名", display=True, display_order=0, json="")
    }
    return render(request, "editor/new_page.html", context)


# 删除页面
def delete_page(request, pid):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    try:
        page = Page.objects.get(id=pid)
        page.delete()
    except Exception as e:
        print(e)
        pass

    return HttpResponseRedirect("/editor/page/")


# 编辑页面
def edit_page(request, pid):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    if request.method == 'POST':
        try:
            title = request.POST['title']
            name = request.POST['name']
            devicesn = int(request.POST['devicesn'])
            template = request.POST['template']
            jsfiles = request.POST['jsfiles']
            cssfiles = request.POST['cssfiles']
            if request.POST['display'] == 'on':
                display = True
            else:
                display = False
            display_order = int(request.POST['display_order'])
            json = request.POST['json']

            try:
                page = Page.objects.get(id=pid)
                page.title = title
                page.name = name
                page.devicesn = devicesn
                page.template = template
                page.jsfiles = jsfiles
                page.cssfiles = cssfiles
                page.display = display
                page.display_order = display_order
                page.json = json
                page.save()
            except Exception as e:
                print(e)

        except Exception as e:
            print(e)

        return HttpResponseRedirect('/editor/page/')

    try:
        page = Page.objects.get(id=pid)
    except Exception as e:
        print(e)
        return HttpResponseRedirect('/editor/page/')

    context = {
        'request': request,
        'templates': get_templates_list(),
        'title': '编辑页面-%d' % pid,
        'page': page
    }
    return render(request, "editor/edit_page.html", context)


# 页面显示序号靠前
def page_order_up(request, pid):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    try:
        page = Page.objects.get(id=pid)
    except Exception as e:
        context = {
            'request': request,
        }
        return render(request, "error/novalidpage.html", context=context)

    page.display_order -= 1
    page.save()
    return HttpResponseRedirect("/editor/page/")


# 页面显示序号靠后
def page_order_down(request, pid):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    try:
        page = Page.objects.get(id=pid)
    except Exception as e:
        context = {
            'request': request,
        }
        return render(request, "error/novalidpage.html", context=context)

    page.display_order += 1
    page.save()
    return HttpResponseRedirect("/editor/page/")


# 页面显示序号靠后
def page_display_toggle(request, pid):
    if request.user.is_anonymous:
        return HttpResponseRedirect("/admin/login/?next=" + request.path)

    try:
        page = Page.objects.get(id=pid)
    except Exception as e:
        context = {
            'request': request,
        }
        return render(request, "error/novalidpage.html", context=context)

    if page.display == True:
        page.display = False
    else:
        page.display = True

    page.save()
    return HttpResponseRedirect("/editor/page/")
