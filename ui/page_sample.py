from django.shortcuts import render
from django.http import *
import ui.mg as mg


def show_location_info(request):
    context = {}
    context['request'] = request
    context['sample'] = mg.get_sample_yx()
    temp = context['sample']

    for state in temp:
        if temp[state] is 0:
            temp[state] = 'OFF'
        elif temp[state] is 1:
            temp[state] = 'ON'

    return render(request,'sample/loaction.html', context=context)

def show_analog_info(request):
    context = {}
    context['request'] = request
    context['sample'] = mg.get_sample_yc()

    return render(request,'sample/analog.html',context=context)