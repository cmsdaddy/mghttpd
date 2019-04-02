# -*- coding: utf8 -*-
from django.urls import path
from django.shortcuts import render
from django.http import *
import ui.models as models
from ui.page_grid import GRID_DATABASE_MODELS
import os
import codecs
import ui.page_collector as collector


def show_develop_main_page(request):
    """
    list all graphic object information in page.
    :param request: HTTP request object
    :return: Django rendered object
    """
    context = dict()

    if request.method == 'GET':
        context['defined_grids_list'] = models.UserDefinedGrid.objects.all()
        context['select_models_list'] = GRID_DATABASE_MODELS
        return render(request, "devel/main.html", context=context)
    else:
        grid_ids = [int(gid) for gid in request.POST.getlist('grid_ids')]
        if len(grid_ids) == 0:
            return HttpResponseRedirect(request.path)

        op = request.POST['operation']
        if op == 'delete':
            for gid in grid_ids:
                models.UserDefinedGrid.objects.get(id=gid).delete()

        elif op == 'disable':
            for gid in grid_ids:
                grid = models.UserDefinedGrid.objects.get(id=gid)
                grid.enabled = False
                grid.save()
        elif op == 'enable':
            for gid in grid_ids:
                grid = models.UserDefinedGrid.objects.get(id=gid)
                grid.enabled = True
                grid.save()
        else:
            pass

        return HttpResponseRedirect(request.path)


def show_faq_page(request):
    context = dict()
    faq_list = list()

    for filename in os.listdir('doc'):
        faq = dict()
        faq['title'] = filename
        with codecs.open('doc/' + filename) as file:
            faq['body'] = file.read()
        faq_list.append(faq)

    context['faq_list'] = faq_list
    return render(request, "devel/FAQ.html", context=context)


develop_url_map = [
    path('', show_develop_main_page),
    path('faq/', show_faq_page),

    path("collector/", collector.urls)
]
urls = (develop_url_map, 'develop', 'develop')
