# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/4 9:12
# File  : urls.py
# Software PyCharm

from django.conf.urls import url
from .views import *

urlpatterns = [

    url(r'^project/$', project_list, name="projects"),
    url(r'^warehouse/$',warehouse_list, name="warehouses"),
    url(r'^tags_list/$',tags_list, name="tags"),
	
    url(r'^update_project/$',update_project),
    url(r'^update_warehouse/$',update_warehouse),
	url(r'^update_tags/$',update_tags),

]
