import json
import time
from django.shortcuts import render
from django.http import *
import ui.models as models
import datetime
from django.urls import path
import ui.cache as cache
from django.db.models import *


def get_all_models_meta():
    models_database = dict()

    for x in dir(models):
        black_list = ['models']

        if x.find('_') == 0:
            continue

        if x in black_list:
            continue

        target = getattr(models, x)

        if issubclass(target, models.models.Model):
            models_database[x] = {
                'model': target,
                'meta': target._meta
            }
    return models_database


GRID_DATABASE_MODELS = get_all_models_meta()


GRID_PREPROCESSORS = {
    "orig": {
        "alias": "原始值",
        "func": lambda v: v,
        "name": "显示值 = 字段值",
    },
    "fun1": {
        "alias": "等比例线性变化",
        "func": lambda self, k: self * k,
        "name": "显示值 = 字段值 * K",
    },
    "fun2": {
        "alias": "等比例线性偏移变化",
        "func": lambda self, k, b: self * k + b,
        "name": "显示值 = 字段值 * K + b",
}
}



def list_all_graphic_object(request):
    """
    list all graphic object information in page.
    :param request: HTTP request object
    :return: Django rendered object
    """
    context = dict()

    if request.method == 'GET':
        context['defined_grids_list'] = models.UserDefinedGrid.objects.all()
        context['select_models_list'] = GRID_DATABASE_MODELS
        return render(request, "94-图形曲线和页面绑定管理/04-图形曲线列表.html", context=context)
    else:
        grid_ids = [int(gid) for gid in request.POST.getlist('grid_ids')]
        if len(grid_ids) == 0:
            return HttpResponseRedirect("/grid/list/")

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

        return HttpResponseRedirect("/grid/list/")


def draw_graphic_page(request, model_name, graphic_name, x_axis_field_name, filters_map,
                      datasources_list, references_list):
    """
    render graphic use gaven parameters
    :param request: HTTP request object
    :param model_name: relation model class name defined in models.py
    :param graphic_name: graphic human-readable name
    :param x_axis_field_name: X-axis bind field defined in model
    :param filters_map: data source filter definitions map
    :param datasources_list: data source definitions list
    :param references_list: reference line definitions list
    :return: Django rendered object
    """
    context = dict()
    now = datetime.datetime.now()

    try:
        range_hour = int(request.GET['range_hour'])
    except:
        range_hour = 6

    try:
        terminal_datetime = request.GET['terminal_datetime']
    except:
        terminal_datetime = 'now'

    context['terminal_datetime'] = terminal_datetime
    context['now'] = now

    if terminal_datetime == 'now':
        terminal_datetime = now
    elif terminal_datetime == 'user_define':
        datetime_str = request.GET['userdefine_terminal_datetime'].replace('T', ' ')
        terminal_datetime = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    else:
        terminal_datetime = now

    context['userdefine_terminal_datetime'] = terminal_datetime
    context['range_hour'] = range_hour

    datetime_begin = terminal_datetime - datetime.timedelta(hours=range_hour)
    print("range hour:", range_hour)
    print("begin datetime:", datetime_begin)
    print("terminal datetime:", terminal_datetime)

    ex_filter = {
        'tsp__gt': datetime_begin,
        'tsp__lte': terminal_datetime
    }
    last_filter = dict(filters_map, **ex_filter)

    datasources_fields_list = list()

    model = GRID_DATABASE_MODELS[model_name]['model']
    records_set = model.objects.filter(**last_filter)

    x_axis_label = [getattr(r, x_axis_field_name) for r in records_set]
    context['x_axis_label'] = x_axis_label

    context['y_axis_list'] = set([d['axis'] for d in datasources_list] + [d['axis'] for d in references_list])
    context['graphic_name'] = graphic_name

    for field in datasources_list:
        func = GRID_PREPROCESSORS[field['processor']]['func']
        param = json.loads(field['processor_param'])
        field['data'] = [func(getattr(r, field['field_name']), *param) for r in records_set]
        datasources_fields_list.append(field)

    context['datasources_fields_list'] = datasources_fields_list
    context['references_list'] = references_list

    return render(request, "94-图形曲线和页面绑定管理/06-曲线渲染显示.html", context=context)


def load_grid_parameters_from_form(form):
    """
    parse some parameters from a GET/POST form
    :param form: GET/POST form object
    :return: parameter dict
    """
    profile = dict()

    model_name = form['model']
    graphic_name = form['graphic_name']
    x_axis_field_name = form['XAxis_datasource']
    print("profile:", model_name, graphic_name, x_axis_field_name)

    # filter
    filters_map = dict()
    filter_id_list = form.getlist('filter_id_list[]')
    for fid in filter_id_list:
        cmp_field = form['filter_compare_key_' + fid]
        cmp_sign = form['filter_compare_sign_' + fid]
        cmp_val = form['filter_compare_value_' + fid]
        print("filter: ", cmp_field, cmp_sign, cmp_val)
        filters_map[cmp_field + cmp_sign] = cmp_val

    # data_source
    datasources_list = list()
    data_source_id_list = form.getlist('datasource_id_list[]')
    for dsid in data_source_id_list:
        field = dict()
        field['axis'] = form['datasource_axis_' + dsid]
        field['field_name'] = form['datasource_key_' + dsid]
        display_name = form['filter_display_name_' + dsid]
        if display_name == '':
            display_name = field['field_name']
        field['display_name'] = display_name

        field['color'] = form['datasource_color_' + dsid]
        field['style'] = form['datasource_style_' + dsid]
        field['width'] = form['datasource_width_' + dsid]
        field['processor'] = form['datasource_preprocess_' + dsid]
        field['processor_param'] = form['datasource_preprocess_param_' + dsid]
        datasources_list.append(field)

    # reference
    references_list = list()
    reference_id_list = form.getlist('reference_id_list[]')
    for rid in reference_id_list:
        ref = dict()
        ref['axis'] = form['reference_axis_' + rid]
        ref['name'] = form['reference_name_' + rid]
        ref['value'] = form['reference_value_' + rid]
        ref['color'] = form['reference_color_' + rid]
        ref['style'] = form['reference_style_' + rid]
        ref['width'] = form['reference_width_' + rid]
        references_list.append(ref)

        print(ref['name'])

    profile['model_name'] = model_name
    profile['graphic_name'] = graphic_name
    profile['x_axis_field_name'] = x_axis_field_name
    profile['filters_map'] = filters_map
    profile['datasources_list'] = datasources_list
    profile['references_list'] = references_list

    return profile


def load_grid_parameters_from_database(gid):
    """
    load all graphic parameter from database use gaven graphic id
    :param gid: graphic id
    :return: <dict> graphic parameter
    """
    obj = models.UserDefinedGrid.objects.get(id=gid)
    profile = {
        'model_name': obj.target,
        'graphic_name': obj.name
    }
    return dict(profile, **json.loads(obj.json_data))


def preview_grid(request):
    """
    preview graphic by request GET form parameters
    :param request: request object
    :return:
    """
    gcache = cache.GraphicPreviewCache()

    try:
        v_key = request.GET['v_key']
        graphic_profile = gcache.get(v_key)
        if graphic_profile is None:
            return render(request, "94-图形曲线和页面绑定管理/08-iframe渲染曲线出错页面.html", {'message': "preview key invalid."})

        return draw_graphic_page(request, **graphic_profile)
    except Exception as e:
        graphic_profile = load_grid_parameters_from_form(request.GET)
        v_key = gcache.set(json.dumps(graphic_profile, ensure_ascii=False))
        preview_url = ''.join([request.path, '?v_key=', v_key, "&control=1"])
        return HttpResponseRedirect(preview_url)


def show_graphic_by_id(request, gid):
    """
    draw graphic by graphic object id stored in database
    :param request: request object
    :param gid: <str> graphic object id
    :return:
    """
    try:
        graphic_profile = load_grid_parameters_from_database(int(gid))
        return draw_graphic_page(request, **graphic_profile)
    except Exception as e:
        context = dict()
        context['message'] = str(e)
        return render(request, "94-图形曲线和页面绑定管理/08-iframe渲染曲线出错页面.html", context=context)


def show_graphic_by_path(request):
    context = dict()

    try:
        binder_list = models.GridPageBinder.objects.filter(path=request.GET['path'])
    except:
        binder_list = list()

    if len(binder_list) == 0:
        return render(request, "94-图形曲线和页面绑定管理/09-iframe未绑定渲染曲线页面.html", context=context)
    elif len(binder_list) == 1:
        grid = binder_list[0].grid
        return show_graphic_by_id(request, grid.id)
    else:
        context = dict()
        context['message'] = "duplicate graphic binding"
        return render(request, "94-图形曲线和页面绑定管理/08-iframe渲染曲线出错页面.html", context=context)


def create_grid_graphic(request):
    """
    create a graphic object
    :param request: HTTP request object.
    :return:
    """
    if request.method == 'GET':
        context = dict()
        try:
            model = request.GET['model']
        except:
            return HttpResponseRedirect("/grid/")

        context['model_name'] = model
        context['model'] = GRID_DATABASE_MODELS[model]
        context['preprocess_list'] = GRID_PREPROCESSORS

        return render(request, "94-图形曲线和页面绑定管理/03-创建新的图形曲线.html", context=context)
    else:
        profile = load_grid_parameters_from_form(request.POST)
        model_name = profile['model_name']
        del profile['model_name']

        graphic_name = profile['graphic_name']
        del profile['graphic_name']

        json_data = json.dumps(profile, ensure_ascii=False)
        now_as_str = time.strftime("%Y-%m-%d %H:%M:%S")

        graphic = models.UserDefinedGrid(name=graphic_name, target=model_name, born=now_as_str, json_data=json_data)
        graphic.save()

        return HttpResponseRedirect("/grid/list/")


def show_grid_page(request):
    context = dict()
    binder_list = models.GridPageBinder.objects.filter(path=request.path)

    context['binder_list'] = binder_list
    context['binder_count'] = binder_list.count()

    return render(request, "94-图形曲线和页面绑定管理/07-系统概要曲线.html", context=context)


def bind_graphic_to_url_path(request):
    if request.method == 'GET':
        context = dict()
        context['defined_grids_list'] = models.UserDefinedGrid.objects.all()
        return render(request, "94-图形曲线和页面绑定管理/01-图形曲线和URL的绑定表单.html", context=context)
    else:
        gid = int(request.POST['gid'])
        target = request.POST['target']

        grid = models.UserDefinedGrid.objects.get(id=gid)
        models.GridPageBinder(grid=grid, path=target).save()
        return HttpResponseRedirect(request.POST['target'])


def grid_and_path_binder_list(request):
    if request.method == 'GET':
        context = dict()
        context['grids_list'] = models.UserDefinedGrid.objects.all()
        context['binder_list'] = models.GridPageBinder.objects.all()
        return render(request, "94-图形曲线和页面绑定管理/02-图形曲线和URL的绑定列表.html", context=context)
    else:
        return HttpResponseRedirect(request.path)


urlpatterns = [
    path('', show_grid_page),
    path('show/<int:gid>/', show_graphic_by_id),
    path('show/', show_graphic_by_path),

    path('preview/', preview_grid),
    path('create/', create_grid_graphic),
    path('list/', list_all_graphic_object),
    path('bind/', bind_graphic_to_url_path),
    path('bind/list/', grid_and_path_binder_list),
]
urls = (urlpatterns, 'grid', 'grid')
