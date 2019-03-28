from django.db import models

# Create your models here.


# 页面模型
class Page(models.Model):
    title = models.CharField(default="[页面标题]", max_length=100, help_text="页面标题内容")
    name = models.CharField(default="[页面名称]", max_length=20, help_text="页面名称内容")
    devicesn = models.IntegerField(default=0, help_text="设备索引编号")
    template = models.TextField(default="default.html", help_text="页面的模板文件")
    jsfiles = models.TextField(default="", blank=True, help_text="这个页面的js文件列表")
    cssfiles = models.TextField(default="", blank=True, help_text="这个页面的css文件列表")
    display = models.BooleanField(default=True, help_text="控制这个页面是否能显示出来")
    display_order = models.IntegerField(default=0, help_text="这个页面在显示栏中的索引位置")
    json = models.TextField(blank=True, help_text="这个页面需要带给js的json数据内容")

    def __str__(self):
        return self.name


# 数据点类型
# string: 字符串; number: 数字
# object: 对象
# object-array: 对象数组; number-arrary： 数字数组; string-array: 字符串数组
class DataPointType(models.Model):
    type = models.CharField(default="类型", max_length=100, help_text="数据点类型")
    name = models.CharField(default="名称", max_length=100, help_text="类型名称")

    def __str__(self):
        return "%s:%s" % (self.name, self.type)


# 数据点模型
class DataPoint(models.Model):
    full_name = models.CharField(default="完整名称", max_length=200, help_text="这个数据点的完整名称")
    short_name = models.CharField(default="名称", max_length=100, help_text="这个数据点的短名称")
    datatype = models.ForeignKey(DataPointType, on_delete=models.CASCADE, help_text="这个数据点的类型")
    access_path = models.TextField(help_text="访问路径")
    k = models.FloatField(default=1.0, help_text="数据点斜率")
    b = models.FloatField(default=0, help_text="数据点偏移")
    mask = models.IntegerField(default=0x7fffffff, help_text="数据点值掩码")
    dot = models.IntegerField(default=0, help_text="小数点位数")
    unit = models.CharField(default="", max_length=20, blank=True, help_text="这个值的显示单位符号")
    max_record = models.IntegerField(default=1, help_text="这个数据点的最大记录条数")
    refer_count = models.IntegerField(default=0, help_text="这个数据点在系统中被引用的次数")

    def __str__(self):
        return self.access_path


# 数据采集器模型
class Collector(models.Model):
    path = models.TextField(default="invalid", help_text="数据点路径")
    def __str__(self):
        return self.path


# 数据点的历史记录模型
class DataPointRecords(models.Model):
    collector = models.ForeignKey(Collector, null=True, on_delete=models.CASCADE, help_text="记录的数据点ID")
    datetime = models.DateTimeField(default="2018-01-01 00:00:00", help_text="记录存储时间")
    record = models.TextField(blank=True, null=True, help_text="记录的数据，用json存储")


# 显示元素类型
# yaoce-遥测 yaoxin-遥信 abstract-摘要 gridx12-图表x12 gridx8-图表x8 gridx6-图表x6 gridx4-图表x4
class ElementType(models.Model):
    type = models.CharField(default="类型", max_length=100, help_text="显示元素类型")
    name = models.CharField(default="名称", max_length=100, help_text="显示元素类型名称")
    width = models.IntegerField(default=12, help_text="这个元素类型的参数值， 主要用于图表宽度确定")

    def __str__(self):
        return "%s:%s" % (self.name, self.type)


# 显示元素
class Element(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    datapoint = models.ManyToManyField(DataPoint, help_text="数据点列表")
    type = models.ForeignKey(ElementType, on_delete=models.CASCADE, help_text="这个元素的类型")
    name = models.CharField(default="名称", max_length=40, help_text="这个元素的名称")
    order = models.IntegerField(default=0, help_text="这个值的显示顺序")
    count = models.IntegerField(default=1, help_text="显示的数据点个数，用于图表显示")
    display = models.BooleanField(default=True, help_text="这个值是否能够显示")

    def __str__(self):
        return self.name


# 历史事件记录
class HistoryRecord(models.Model):
    # system, user, bms, pcs, pv, bg 等等，根据实际需求自主定义
    kind = models.CharField(default="system", max_length=60, help_text="类型名称")
    code = models.IntegerField(default=0, blank=True, null=True, help_text="事件代码")
    datetime = models.DateTimeField(default="2018-01-01 00:00:00.000", help_text="事件产生时戳")
    master = models.IntegerField(default=0, blank=True, null=True, help_text="设备主索引号")
    slave = models.IntegerField(default=0, blank=True, null=True, help_text="设备次索引号")
    body = models.TextField(default="无", help_text="事件内容")
    user = models.CharField(default="root", max_length=30, help_text="事件记录人")


# 系统记录表
class SystemRecord(models.Model):
    key = models.TextField(default="untitled", max_length=100, help_text="键名")
    value = models.TextField(default="value", max_length=4096, help_text="键值")


#=================================以下为统计报表模型================================================
class PCSYaoce(models.Model):
    pcsid = models.IntegerField(default=0)
    tsp = models.DateTimeField(default='2018-01-01 00:00:00.000')
    
    dc_power = models.IntegerField(default=0)

    dc_voltage = models.IntegerField(default=0)
    dc_current = models.IntegerField(default=0)

    grid_freq = models.IntegerField(default=0)

    Vab = models.IntegerField(default=0)
    Vbc = models.IntegerField(default=0)
    Vca = models.IntegerField(default=0)

    Ia = models.IntegerField(default=0)
    Ib = models.IntegerField(default=0)
    Ic = models.IntegerField(default=0)

    year_discharge_kwh_total = models.IntegerField(default=0)
    year_discharge_time_total = models.IntegerField(default=0)

    charge_kwh_total = models.IntegerField(default=0)
    discharge_kwh_total = models.IntegerField(default=0)

    day_charge_kwh_total = models.IntegerField(default=0)
    day_discharge_kwh_total = models.IntegerField(default=0)

    day_charge_time_total = models.IntegerField(default=0)
    day_discharge_time_total = models.IntegerField(default=0)

    month_charge_kwh_total = models.IntegerField(default=0)
    month_discharge_kwh_total = models.IntegerField(default=0)

    month_charge_time_total = models.IntegerField(default=0)
    month_discharge_time_total = models.IntegerField(default=0)

    charge_count = models.IntegerField(default=0)
    discharge_count = models.IntegerField(default=0)

    year_charge_time_total = models.IntegerField(default=0)
    year_charge_kwh_total = models.IntegerField(default=0)

    charge_time_total = models.IntegerField(default=0)
    discharge_time_total = models.IntegerField(default=0)

    #def __str__(self):
    #    return self.pcsid

    class Meta:
        db_table = "PCSYaoce"


class BMSYaoce(models.Model):
    bmsid = models.IntegerField(default=0)
    tsp = models.DateTimeField(default='2018-01-01 00:00:00.000')
    bat_gid_of_min_temp = models.IntegerField(default=0)
    bat_gid_of_max_temp = models.IntegerField(default=0)
    bat_gid_of_min_voltage = models.IntegerField(default=0)
    bat_gid_of_max_voltage = models.IntegerField(default=0)
    bat_min_temp = models.IntegerField(default=0)
    bat_max_temp = models.IntegerField(default=0)
    bat_min_voltage = models.IntegerField(default=0)
    bat_max_voltage = models.IntegerField(default=0)
    SOC = models.IntegerField(default=0)
    SOH = models.IntegerField(default=0)
    chargable_kwh = models.IntegerField(default=0)
    dischargable_kwh = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    voltage = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    total_charged_kwh = models.IntegerField(default=0)
    total_discharged_kwh = models.IntegerField(default=0)

    #def __str__(self):
    #    return self.bmsid

    class Meta:
        db_table = "BMSYaoce"


class BMSGroupYaoce(models.Model):
    bmsid = models.IntegerField(default=0)
    bmsgid = models.IntegerField(default=0)
    tsp = models.DateTimeField(default='2018-01-01 00:00:00.000')
    bat_gid_of_min_temp = models.IntegerField(default=0)
    bat_gid_of_max_temp = models.IntegerField(default=0)
    bat_gid_of_min_voltage = models.IntegerField(default=0)
    bat_gid_of_max_voltage = models.IntegerField(default=0)
    bat_min_temp = models.IntegerField(default=0)
    bat_max_temp = models.IntegerField(default=0)
    bat_min_voltage = models.IntegerField(default=0)
    bat_max_voltage = models.IntegerField(default=0)
    SOC = models.IntegerField(default=0)
    SOH = models.IntegerField(default=0)
    chargable_kwh = models.IntegerField(default=0)
    dischargable_kwh = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    voltage = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    total_charged_kwh = models.IntegerField(default=0)
    total_discharged_kwh = models.IntegerField(default=0)

    class Meta:
        db_table = "BMSGroupYaoce"


class CurrentError(models.Model):
    """系统当前故障模型"""
    ueid = models.CharField(max_length=30, help_text="故障唯一ID号，和历史故障ID号公用")
    ecode = models.TextField(help_text="故障代码")
    abstrct = models.TextField(help_text="故障摘要信息")
    econtext = models.TextField(help_text="故障详细内容，存储格式为json")
    eclass = models.CharField(max_length=100, help_text="故障类型")
    elevel = models.IntegerField(help_text="故障级别")
    etsp = models.DateTimeField(default='2018-01-01 00:00:00', help_text="故障产生时间")

    class Meta:
        db_table = "CurrentError"


class HistoryError(models.Model):
    """系统历史故障模型"""
    ueid = models.CharField(max_length=30, help_text="故障唯一ID号，从当前故障号继承")
    ecode = models.TextField(help_text="故障代码")
    abstrct = models.TextField(help_text="故障摘要信息")
    econtext = models.TextField(help_text="故障详细内容，存储格式为json")
    eclass = models.CharField(max_length=100, help_text="故障类型")
    elevel = models.IntegerField(help_text="故障级别")
    etsp_begin = models.DateTimeField(default='2018-01-01 00:00:00', help_text="故障产生时间")
    etsp_end = models.DateTimeField(default='2018-01-01 00:00:00', help_text="故障处理时间")

    econfirm_tsp = models.DateTimeField(default='2018-01-01 00:00:00', help_text="故障确认时间")
    econfirm_user = models.CharField(default="nobody", max_length=100, help_text="故障确认人员")
    econfirm_sign = models.TextField(help_text="故障确认签名及原因备注说明")

    class Meta:
        db_table = "HistoryError"


class UserDefinedGrid(models.Model):
    name = models.CharField(max_length=1024, default='default name')
    enabled = models.BooleanField(default=True)
    born = models.DateTimeField(default='2019-01-01 00:00:00')
    target = models.CharField(max_length=100, default='None')
    json_data = models.TextField(default="")

    class Meta:
        db_table = "UserDefinedGrid"


class GridPageBinder(models.Model):
    grid = models.ForeignKey(UserDefinedGrid, on_delete=models.CASCADE)
    path = models.CharField(max_length=512, default="/grid/")

    class Meta:
        db_table = "GridPageBinder"

