# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/7/26 17:02
# File  : urls.py
# Software PyCharm

from django.conf.urls import url
from .views import host_unit_list, add_host_unit, edit_host_unit, del_host_unit, \
get_container_by_group, container_env_list, add_container_env, del_container_env, \
edit_container_env, container_env_group, add_container_env_group, del_container_env_group, \
edit_container_group_env

urlpatterns = [
    url(r'^host_unit_list/$', host_unit_list, name="hostunit"),
    url(r'^add_host_unit/$', add_host_unit, name="addhostunit"),
    url(r'^edit_host_unit/$', edit_host_unit, name="edithostunit"),
    url(r'^del_host_unit/$', del_host_unit, name="delhostunit"),
    url(r'get_container_by_group', get_container_by_group, name="getcontainer"),

    url(r'^container_env_list/$', container_env_list, name="envlist"),
    url(r'^add_container_env/$', add_container_env, name="addenv"),
    url(r'^del_container_env/$', del_container_env, name="delenv"),
    url(r'^edit_container_env/$', edit_container_env, name="editenv"),

    url(r'^container_env_group/$', container_env_group, name="genvlist"),
    url(r'^add_container_env_group/$', add_container_env_group, name="gaddenv"),
    url(r'^del_container_env_group/$', del_container_env_group, name="gdelenv"),
    url(r'^edit_container_group_env/$', edit_container_group_env, name="geditenv"),
]
