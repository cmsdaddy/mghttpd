# -*- coding: utf8 -*-
from django.shortcuts import render
from django.http import *
from django.urls import path, reverse
from django.utils.datastructures import MultiValueDictKeyError
import random
import time
import logging
import json
import os
import uuid
import codecs
import ui.scada as scada
import ui.mg as mg
import threading

filename = 'save.json'
linkage_profile_dir = scada.profile_dir_path + '/linkage'
if not os.path.exists(linkage_profile_dir):
    logging.info("检测到一次图文件存放目录不存在, 自动创建目录: {}".format(linkage_profile_dir))
    os.mkdir(linkage_profile_dir, 0o777)

linkage_trash_dir = scada.trash_dir_path + '/linkage'
if not os.path.exists(linkage_trash_dir):
    logging.info("检测到一次图文件回收目录不存在, 自动创建目录: {}".format(linkage_trash_dir))
    os.mkdir(linkage_trash_dir, 0o777)


linkage_default_img = '/static/linkage.png'


# Create your views here.
def show_editor_page(request):
    return render(request, "95-系统一次图编辑显示管理/editor.html")


def show_preview_page(request):
    return render(request, "95-系统一次图编辑显示管理/preview.html")


def edit_models(request):

    if request.method == 'GET':
        try:
            with codecs.open(filename, encoding='utf8') as file:
                return HttpResponse(file.read())
        except:
            return JsonResponse({})
    else:
        with codecs.open(filename, mode="w", encoding='utf8') as file:
            obj = json.loads(request.body.decode())
            file.write(json.dumps(obj, ensure_ascii=False, indent=2))

        return JsonResponse({"status": "ok"})


def show_change_model_page(request, id):
    with codecs.open(filename, encoding='utf8') as file:
        all_models = json.loads(file.read())
        model = [model for model in all_models['models'] if model['id'] == id][0]

    if request.method == 'POST':
        print(request.POST)
        try:
            model['style']['row'] = int(request.POST['row'])
        except:
            model['style']['row'] = 0

        try:
            model['style']['column'] = int(request.POST['column'])
        except:
            model['style']['column'] = 0

        try:
            model['style']['library'] = int(request.POST['library'])
        except:
            model['style']['library'] = all_models['libraries'][0]['id']

        try:
            model['style']['v_scale'] = int(request.POST['v_scale'])
        except KeyError:
            model['style']['v_scale'] = 1

        try:
            model['style']['h_scale'] = int(request.POST['h_scale'])
        except KeyError:
            model['style']['h_scale'] = 1

        try:
            model['style']['degree'] = float(request.POST['degree'])
        except:
            model['style']['degree'] = 0

        # 外框控制
        model['style']['show_boarder'] = True if int(request.POST['show_boarder']) > 0 else False

        with codecs.open(filename, mode="w", encoding='utf8') as file:
            file.write(json.dumps(all_models, ensure_ascii=False, indent=2))

        return HttpResponseRedirect('/')

    return render(request, "95-系统一次图编辑显示管理/model_change_form.html", context={"model": model, "all_model": all_models})


def get_linkage_profile_full_path(lid):
    return '/'.join([linkage_profile_dir, lid])


def read_linkage_profile(lid):
    full_file_path = get_linkage_profile_full_path(lid)
    if not os.path.exists(full_file_path):
        raise FileNotFoundError

    print("++ read_linkage_profile", time.time(), threading.get_ident())

    with codecs.open(full_file_path, encoding='utf8') as file:
        linkage = json.load(file)

    print("-- read_linkage_profile", time.time(), threading.get_ident())

    return linkage


def write_linkage_profile(lid, profile):
    full_file_path = get_linkage_profile_full_path(lid)

    print("++ write_linkage_profile", time.time())

    try:
        with codecs.open(full_file_path, mode='w', encoding='utf8') as file:
            json.dump(profile, file, ensure_ascii=False, indent=2)
    except json.decoder.JSONDecodeError:
        print("JSONDecodeError")
    finally:
        print("11111111")

    print("-- write_linkage_profile", time.time())

    return profile


def merge_linkage_profile(lid, profile):
    try:
        old_profile = read_linkage_profile(lid)
        new_profile = dict(old_profile, **profile)
    except FileNotFoundError:
        new_profile = profile

    return write_linkage_profile(lid, new_profile)


def show_all_linage_profile(request):
    context = dict()
    linkage_profiles_list = list()

    for f in os.listdir(linkage_profile_dir):
        with codecs.open(linkage_profile_dir + '/' + f, encoding='utf8') as file:
            linkage_profiles_list.append(json.load(file))

    context['linkage_profiles_list'] = linkage_profiles_list
    return render(request, "95-系统一次图编辑显示管理/02-list-显示全部一次图方案文件列表.html", context=context)


def create_new_linage_profile(request):
    if request.method == 'GET':
        context = dict()
        try:
            context['id'] = request.GET['id']
        except MultiValueDictKeyError:
            context['id'] = uuid.uuid4()
        return render(request, "95-系统一次图编辑显示管理/01-form-编辑一次图方案文件.html", context=context)
    else:
        lid = request.POST['id']
        profile = {
            'id': lid,
            'name': request.POST['name'],
            'width': int(request.POST['width']),
            'height': int(request.POST['height']),
            'background_color': request.POST['background_color'],
        }

        write_linkage_profile(lid, profile)
        try:
            next_url = request.GET['next']
        except MultiValueDictKeyError:
            next_url = reverse("list linkage profile")

        return HttpResponseRedirect(next_url)


def edit_linkage_profile(request, lid):
    context = dict()
    if request.method == 'GET':
        try:
            context = read_linkage_profile(lid)
        except FileNotFoundError:
            context['id'] = lid
            logging.warning("id={}的一次图方案文件不存在，自动创建并开始编辑".format(lid))

        return render(request, "95-系统一次图编辑显示管理/01-form-编辑一次图方案文件.html", context=context)
    else:
        profile = {
            'name': request.POST['name'],
            'width': int(request.POST['width']),
            'height': int(request.POST['height']),
            'background_color': request.POST['background_color'],
        }
        merge_linkage_profile(lid, profile)

        try:
            next_url = request.GET['next']
        except MultiValueDictKeyError:
            next_url = reverse("list linkage profile")

        return HttpResponseRedirect(next_url)


def delete_linkage_profile(request, lid):
    full_file_path = get_linkage_profile_full_path(lid)
    logging.debug("request: {}, want delete linkage profile: {}".format(request, lid))

    if os.path.exists(full_file_path):
        os.remove(full_file_path)

    try:
        next_url = request.GET['next']
    except MultiValueDictKeyError:
        next_url = reverse("list linkage profile")

    return HttpResponseRedirect(next_url)


def design_linkage_profile(request, lid):
    context = dict()
    try:
        context['profile'] = read_linkage_profile(lid)
    except FileNotFoundError:
        context['id'] = lid
        return render(request, "95-系统一次图编辑显示管理/00-error-设计的文件不存在.html", context=context)

    return render(request, "95-系统一次图编辑显示管理/02-设计一次图方案内容.html", context=context)


def save_linkage_profile(request, lid):
    try:
        next_url = request.GET['next']
    except MultiValueDictKeyError:
        next_url = reverse("list linkage profile")

    return HttpResponseRedirect(next_url)


def process_linkage_object_as_json(request, lid, kind):
    context = dict()
    if request.method == 'GET':
        try:
            profile = read_linkage_profile(lid)
            objs = profile[kind]
        except FileNotFoundError:
            context['id'] = lid
            return render(request, "95-系统一次图编辑显示管理/00-error-设计的文件不存在.html", context=context)
        except KeyError:
            objs = dict()

        return JsonResponse(objs, safe=False)
    else:
        try:
            profile = read_linkage_profile(lid)
        except FileNotFoundError:
            context['id'] = lid
            return render(request, "95-系统一次图编辑显示管理/00-error-设计的文件不存在.html", context=context)

        try:
            _ = profile[kind]
        except KeyError:
            profile[kind] = dict()

        obj = json.loads(request.POST['obj'], encoding='utf8')
        profile[kind][obj['id']] = obj
        write_linkage_profile(lid, profile)
        return HttpResponseRedirect(request.path)


def linkage_profile_as_json(request, lid):
    context = dict()

    if request.method == 'GET':
        try:
            profile = read_linkage_profile(lid)
            return JsonResponse(profile, safe=False)
        except FileNotFoundError:
            context['id'] = lid
            return render(request, "95-系统一次图编辑显示管理/00-error-设计的文件不存在.html", context=context)
    else:
        profile = json.loads(request.POST['profile'], encoding='utf8')
        write_linkage_profile(lid, profile)
        return HttpResponseRedirect(request.path)


def linkage_collector_value_as_json(request, lid):
    try:
        profile = read_linkage_profile(lid)
    except FileNotFoundError:
        return JsonResponse({"status": "error", "reason": "solution file not found"}, safe=False)

    try:
        models = profile['models']
    except KeyError:
        return JsonResponse({"status": "error", "reason": "collector not available"}, safe=False)

    data = dict()
    collector = dict(status='ok', data=data)
    datasource_map = dict()
    for nid, model in models.items():
        if model['datasource'] == '':
            continue

        p = model['datasource']
        try:
            datasource_map[p].append(nid)
        except KeyError:
            datasource_map[p] = [nid]

    for p in datasource_map.keys():
        value = mg.read(p)
        for nid in datasource_map[p]:
            data[nid] = value

    return JsonResponse(collector, safe=False)


def linkage_models_as_json(request, lid):
    return process_linkage_object_as_json(request, lid, 'models')


def linkage_links_as_json(request, lid):
    return process_linkage_object_as_json(request, lid, 'links')


def linkage_anchors_as_json(request, lid):
    return process_linkage_object_as_json(request, lid, 'anchors')


def linkage_libraries_as_json(request, lid):
    return process_linkage_object_as_json(request, lid, 'libraries')


def linkage_events_as_json(request, lid):
    return process_linkage_object_as_json(request, lid, 'events')


def linkage_functions_as_json(request, lid):
    return process_linkage_object_as_json(request, lid, 'functions')


def linkage_link_edit(request, lid, linkid):
    """编辑连线详细内容"""
    context = dict()

    if request.method == 'GET':
        try:
            context['lid'] = lid
            context['linkid'] = linkid
            links = read_linkage_profile(lid)['links']
        except FileNotFoundError:
            context['id'] = lid
            return render(request, "95-系统一次图编辑显示管理/00-error-设计的文件不存在.html", context=context)
        except KeyError:
            context['id'] = lid
            return render(request, "95-系统一次图编辑显示管理/00-error-节点不存在.html", context=context)

        context['link'] = links[linkid]
        return render(request, "95-系统一次图编辑显示管理/02-连接/00-form-连线编辑.html", context=context)
    else:
        profile = read_linkage_profile(lid)
        try:
            links = profile['links']
        except KeyError:
            links = dict()
            profile['links'] = links

        try:
            link = links[linkid]
        except KeyError:
            link = dict()
            links[linkid] = link

        link['id'] = linkid
        link['title'] = request.POST['title']
        link['color'] = request.POST['color']
        link['width'] = int(request.POST['width'])
        link['style'] = request.POST['style']

        write_linkage_profile(lid, profile)
        return HttpResponseRedirect(request.GET['next'])


def linkage_model_edit(request, lid, nid):
    """编辑模型详细内容"""
    context = dict()

    if request.method == 'GET':
        try:
            models = read_linkage_profile(lid)['models']
        except FileNotFoundError:
            context['id'] = lid
            return render(request, "95-系统一次图编辑显示管理/00-error-设计的文件不存在.html", context=context)
        except KeyError:
            context['id'] = lid
            context['nid'] = nid
            return render(request, "95-系统一次图编辑显示管理/00-error-节点不存在.html", context=context)

        context['id'] = lid
        context['model'] = models[nid]
        return render(request, "95-系统一次图编辑显示管理/01-节点/00-form-节点编辑.html", context=context)

    try:
        profile = read_linkage_profile(lid)
    except FileNotFoundError:
        context['id'] = lid
        return render(request, "95-系统一次图编辑显示管理/00-error-设计的文件不存在.html", context=context)

    try:
        model = profile['models'][nid]
    except KeyError:
        model = dict(id=nid)
        profile['models'][nid] = model

    model['name'] = request.POST['name']
    model['width'] = int(request.POST['width'])
    model['height'] = int(request.POST['height'])
    model['title'] = request.POST['title']
    model['comment'] = request.POST['comment']
    model['show_boarder'] = True if request.POST['show_boarder'] == 'true' else False
    model['font_size'] = int(request.POST['font_size'])
    model['font_color'] = request.POST['font_color']
    model['datasource'] = request.POST['datasource']
    model['init_value'] = request.POST['init_value']
    model['href'] = request.POST['href']

    write_linkage_profile(lid, profile)
    return HttpResponseRedirect(request.GET['next'])


def linkage_model_vmap_edit(request, lid, nid, vid):
    if request.method == 'GET':
        context = dict()

        try:
            models = read_linkage_profile(lid)['models']
        except FileNotFoundError:
            context['id'] = lid
            return render(request, "95-系统一次图编辑显示管理/00-error-设计的文件不存在.html", context=context)
        except KeyError:
            context['id'] = lid
            context['nid'] = nid
            return render(request, "95-系统一次图编辑显示管理/00-error-节点不存在.html", context=context)

        context['lid'] = lid
        context['nid'] = nid
        context['vid'] = vid
        context['model'] = models[nid]

        solution_lib_path = scada.linkage_source_path + '/' + lid
        try:
            context['lib_img_list'] = os.listdir(solution_lib_path)
        except FileNotFoundError:
            context['lib_img_list'] = list()

        linkage_lib_path = scada.linkage_source_path + '/library'
        try:
            context['linkage_lib_img_list'] = os.listdir(linkage_lib_path)
        except FileNotFoundError:
            os.mkdir(linkage_lib_path, 0o777)

        try:
            context['vmap'] = models[nid]['vmap'][vid]
        except KeyError:
            context['vmap'] = dict(id=vid)

        return render(request, "95-系统一次图编辑显示管理/01-节点/01-form-显示值映射.html", context=context)
    else:
        profile = read_linkage_profile(lid)
        node = profile['models'][nid]

        try:
            vmap = node['vmap']
        except KeyError:
            vmap = dict()
            node['vmap'] = vmap

        try:
            vm = vmap[vid]
        except KeyError:
            vm = dict(id=vid)
            vmap[vid] = vm

        vm['value'] = request.POST['value']
        vm['h_scale'] = int(request.POST['h_scale'])
        vm['v_scale'] = int(request.POST['v_scale'])
        vm['degree'] = float(request.POST['degree'])
        vm['name'] = request.POST['name']
        vm['href'] = request.POST['href']

        try:
            lib_img = request.POST['lib_img']
        except:
            lib_img = ''

        if lib_img == '':
            solution_source_dir = scada.linkage_source_path + '/' + lid
            if not os.path.exists(solution_source_dir):
                os.mkdir(solution_source_dir, 0o777)

            try:
                img = request.FILES['img']
                vmap_image_path = solution_source_dir + '/' + vid + '-' + img.name
                vm['img'] = vmap_image_path[len(scada.static_dir_path)-len('/static'):]

                with codecs.open(vmap_image_path, mode='wb') as file:
                    for chunk in img.chunks():
                        file.write(chunk)
            except:
                if 'img' not in vm:
                    vm['img'] = ''
        else:
            vm['img'] = lib_img

        write_linkage_profile(lid, profile)
        return HttpResponseRedirect(request.GET['next'])


def linkage_model_vmap_delete(request, lid, nid, vid):
    profile = read_linkage_profile(lid)
    del profile['models'][nid]['vmap'][vid]
    write_linkage_profile(lid, profile)
    return HttpResponseRedirect(request.GET['next'])


def linkage_model_vmap_create(request, lid, nid):
    if request.method == 'GET':
        return linkage_model_vmap_edit(request, lid, nid, uuid.uuid4())
    else:
        return linkage_model_vmap_edit(request, lid, nid, request.POST['id'])


def show_linkage_page(request, lid):
    profile = read_linkage_profile(lid)
    return render(request, "95-系统一次图编辑显示管理/04-显示方案内容.html", context={'profile': profile})


def preview_linkage_page(request, lid):
    profile = read_linkage_profile(lid)
    return render(request, "95-系统一次图编辑显示管理/03-预览方案内容.html", context={'profile': profile})


def get_actived_linkage():
    actived = None

    for f in os.listdir(linkage_profile_dir):
        with codecs.open(linkage_profile_dir + '/' + f, encoding='utf8') as file:
            profile = json.load(file)
            if actived is None:
                actived = profile

            try:
                if profile['actived'] is True:
                    actived = profile
            except KeyError:
                pass

    return actived


def list_all_user_defined_inode(request):
    pass


def new_user_defined_inode(request):
    return render(request, "95-系统一次图编辑显示管理/03-库文件/")


def edit_user_defined_inode(request, iid):
    pass


urlpatterns = [
    path('', show_all_linage_profile),
    path('edit/', show_editor_page),
    path('preview/', show_preview_page),

    # 显示方案内容
    path('show/<str:lid>/', show_linkage_page, name="display linkage page"),
    path('preview/<str:lid>/', preview_linkage_page, name="preview linkage page"),

    path('model/<int:id>/change/', show_change_model_page),
    path('json/', edit_models),

    # 将方案全都返回
    path('<str:lid>/json/', linkage_profile_as_json, name="linkage profile json"),
    # 将方案变量值全都返回
    path('<str:lid>/collector/', linkage_collector_value_as_json, name="linkage collector value json"),

    # 将方案中的节点全都放回
    path('models/<str:lid>/json/', linkage_models_as_json, name="linkage node json"),
    # 将方案中的锚点全都返回
    path('anchors/<str:lid>/json/', linkage_anchors_as_json, name="linkage anchors json"),
    # 将方案中的连接全都返回
    path('links/<str:lid>/json/', linkage_links_as_json, name="linkage links json"),
    # 将方案中的库全都返回
    path('libraries/<str:lid>/json/', linkage_libraries_as_json, name="linkage libraries json"),
    # 将方案中的事件全都返回
    path('events/<str:lid>/json/', linkage_events_as_json, name="linkage events json"),
    # 将方案中的函数全都返回
    path('functions/<str:lid>/json/', linkage_functions_as_json, name="linkage functions json"),

    # 编辑节点的详细属性
    path('<str:lid>/model/<str:nid>/edit/', linkage_model_edit, name="edit linkage node"),
    # 编辑连线的详细属性
    path('<str:lid>/link/<str:linkid>/edit/', linkage_link_edit, name="edit linkage link"),

    # 编辑节点的映射值
    path('<str:lid>/model/<str:nid>/vmap/<str:vid>/edit/', linkage_model_vmap_edit, name="edit node v_map"),
    path('<str:lid>/model/<str:nid>/vmap/<str:vid>/delete/', linkage_model_vmap_delete, name="delete node v_map"),
    path('<str:lid>/model/<str:nid>/vmap/create', linkage_model_vmap_create, name="create node v_map"),

    path("list/", show_all_linage_profile, name="list linkage profile"),
    path("create/", create_new_linage_profile, name="create linkage profile"),
    path("edit/<str:lid>/", edit_linkage_profile, name="edit linkage profile"),
    path("delete/<str:lid>/", delete_linkage_profile, name="delete linkage profile"),

    path("design/<str:lid>/", design_linkage_profile, name="design linkage profile"),
    path("design/<str:lid>/save/", save_linkage_profile, name="save linkage profile"),
]

urls = (urlpatterns, "linkage", "linkage")
