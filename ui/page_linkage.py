# -*- coding: utf8 -*-
from django.shortcuts import render
from django.http import *
from django.urls import path
from ui.models import *
from django.db.models import *
import os
import ui.mg as mg
import random
import ui.api as api
from ui import page
import time
import json
import codecs


filename = 'save.json'


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


urlpatterns = [
    path('', show_linkage_page),
    path('edit/', show_editor_page),
    path('preview/', show_preview_page),
    path('show/', show_linkage_page),

    path('model/<int:id>/change/', show_change_model_page),
    path('json/', edit_models),
]

urls = (urlpatterns, "linkage", "linkage")