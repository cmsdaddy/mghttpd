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


filename = 'save.json'
linkage_profile_dir = scada.profile_dir_path + '/linkage'
if not os.path.exists(linkage_profile_dir):
    logging.info("检测到一次图文件存放目录不存在, 自动创建目录: {}".format(linkage_profile_dir))
    os.mkdir(linkage_profile_dir, 0o777)

linkage_trash_dir = scada.trash_dir_path + '/linkage'
if not os.path.exists(linkage_trash_dir):
    logging.info("检测到一次图文件回收目录不存在, 自动创建目录: {}".format(linkage_trash_dir))
    os.mkdir(linkage_trash_dir, 0o777)


# Create your views here.
def show_editor_page(request):
    return render(request, "95-系统一次图编辑显示管理/editor.html")


def show_preview_page(request):
    return render(request, "95-系统一次图编辑显示管理/preview.html")


def show_linkage_page(request):
    return render(request, "95-系统一次图编辑显示管理/show.html")


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

    with codecs.open(full_file_path, encoding='utf8') as file:
        linkage = json.load(file)

    return linkage


def write_linkage_profile(lid, profile):
    full_file_path = get_linkage_profile_full_path(lid)

    with codecs.open(full_file_path, mode='w', encoding='utf8') as file:
        json.dump(profile, file, ensure_ascii=False, indent=2)

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


urlpatterns = [
    path('', show_linkage_page),
    path('edit/', show_editor_page),
    path('preview/', show_preview_page),
    path('show/', show_linkage_page),

    path('model/<int:id>/change/', show_change_model_page),
    path('json/', edit_models),

    path("list/", show_all_linage_profile, name="list linkage profile"),
    path("create/", create_new_linage_profile, name="create linkage profile"),
    path("edit/<str:lid>/", edit_linkage_profile, name="edit linkage profile"),
    path("delete/<str:lid>/", delete_linkage_profile, name="delete linkage profile"),

    path("design/<str:lid>/", design_linkage_profile, name="design linkage profile"),
    path("design/<str:lid>/save/", save_linkage_profile, name="save linkage profile"),
]

urls = (urlpatterns, "linkage", "linkage")
