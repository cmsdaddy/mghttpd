from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import os
import ui.mg as mg
import random
import ui.api as api
import time
import json


def multipage_processor(records, show_page, show_count, filter=None):
    """多分页处理"""
    context = dict()

    # 记录总条数
    records_count = records.count()
    context['records_count'] = records_count

    # 可显示页面数量
    if records_count % show_count == 0:
        pages_count = int(records_count / show_count)
    else:
        pages_count = int(records_count / show_count) + 1
    context['pages_count'] = pages_count
    context['show_page'] = show_page
    context['page_number'] = pages_count - 1

    if pages_count <= 1:
        context['page_list'] = []
    else:
        page_list = []
        if show_page >= 10:
            page_begin = show_page - 10
        else:
            page_begin = 0

        if page_begin + 20 >= pages_count:
            page_end = pages_count
        else:
            page_end = page_begin + 19

        context['page_list'] = [page for page in range(page_begin, page_end)]

    begin = show_page * show_count
    if begin + show_count > records_count:
        end = records_count + 1
    else:
        end = begin + show_count + 1
    context['begin'] = begin
    context['end'] = end

    # 选出范围内的记录
    records_list = records.order_by('-id')[begin: end]
    context['records_list'] = records_list

    return context
