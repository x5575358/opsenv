# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/7 14:35
# File  : urls.py
# Software PyCharm

from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^list/$',asset_list, name="ec2infolist"),
    url(r'^ec2usedlist/$',show_Ec2_Cpu_Network_Used, name="ec2usedlist"),
    url(r'^downec2usedlist/$',accord_time_range_down_files, name="downec2usedlist"),
#    url(r'^get_ec2_info/$',get_ec2_info,name="ec2"),
    url(r'^show_alb_info/$',show_alb_info,name="albinfolist"),
    url(r'^show_rds_info/$',show_rds_info,name="rdsinfolist"),

    url(r'^api_get_ec2_info/$',zabbix_create_template_need_data_invoke, name="apiec2info"),
]
