# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/7/3 13:38
# File  : urls.py
# Software PyCharm


from django.conf.urls import url
from .views import change_recoder, add_change, sealing_release, apply_change_list, apply_change

urlpatterns = [
    url(r'^change_recoder/$', change_recoder, name="mchange_list"),
    url(r'^add_change/$', add_change, name="change"),
    url(r'^sealing_release/$', sealing_release, name="sealrelease"),
    url(r'^apply_change_list/$', apply_change_list, name="mchange_apply_list"),
    url(r'^apply_change/$', apply_change, name="mchaneg_apply_change"),
]
