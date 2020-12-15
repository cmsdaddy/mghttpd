from django.db import models

# Create your models here.

# 历史事件记录
class HistoryRecord(models.Model):
    # system, user, bms, pcs, pv, bg 等等，根据实际需求自主定义
    kind = models.CharField(default="system", max_length=60, help_text="类型名称")
    code = models.IntegerField(default=0, blank=True, null=True, help_text="事件代码")
    datetime = models.DateTimeField(default="2018-01-01 00:00:00.000", help_text="事件产生时戳")
    main = models.IntegerField(default=0, blank=True, null=True, help_text="设备主索引号")
    subordinate = models.IntegerField(default=0, blank=True, null=True, help_text="设备次索引号")
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

