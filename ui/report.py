# -*- coding: utf8 -*-
import datetime


def report_bms_device(begin, end):
    pass


def report_pcs_device(begin, end):
    pass


# run every single day at 00:00
def generate_day_report():
    now = datetime.datetime.now()
    refer = datetime.datetime(year=now.year, month=now.month, day=now.day) - datetime.timedelta(days=1)

    begin = refer.strftime("%Y-%m-%d 00:00:00.000000")
    end = refer.strftime("%Y-%m-%d 23:59:59:999999")

    print("report range from", begin, "to", end)


# run every month @ day 01 00:00:00
def generate_month_report():
    now = datetime.datetime.now()
    refer = datetime.datetime(year=now.year, month=now.month, day=now.day) - datetime.timedelta(days=1)

    begin = refer.strftime("%Y-%m-%d 00:00:00.000000")
    end = refer.strftime("%Y-%m-%d 23:59:59:999999")

    print("report range from", begin, "to", end)


# run every year @ 01-01 00:00:00
def generate_year_report():
    pass


if __name__ == '__main__':
    generate_day_report()
