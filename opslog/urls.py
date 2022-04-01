# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/8 11:14
# File  : urls.py
# Software PyCharm

from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^list/',loglist),
    url(r'^async_log_list/',async_log_list , name="async"),
    url(r'^scanf_async_log/', sacnf_async_log, name="scanf"),
    url(r'^login_log_list/', login_log_list, name="login_log"),
    url(r'^tools_restart_log/', restart_tools_log, name="toolslog"),
    url(r'^exec_script_group/', exec_script_group, name="excescriptgroup"),
]
