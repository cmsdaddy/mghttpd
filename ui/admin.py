from django.contrib import admin

# Register your models here.
from ui.models import *


class DataPointTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'name')


admin.site.register(DataPointType, DataPointTypeAdmin)


class DataPointAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'datatype', 'access_path', 'k', 'b', 'mask', 'dot', 'unit', 'max_record')


admin.site.register(DataPoint, DataPointAdmin)


class CollectorAdmin(admin.ModelAdmin):
    list_display = ('id', 'path')


admin.site.register(Collector, CollectorAdmin)


class DataPointRecordsAdmin(admin.ModelAdmin):
    list_display = ('collector', 'datetime', 'record')


admin.site.register(DataPointRecords, DataPointRecordsAdmin)


class ElementTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'name')


admin.site.register(ElementType, ElementTypeAdmin)


class ElementAdmin(admin.ModelAdmin):
    list_display = ('page', 'type', 'name', 'order', 'count', 'display')


admin.site.register(Element, ElementAdmin)
