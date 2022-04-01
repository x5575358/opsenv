# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/4 13:44
# File  : urls.py
# Software PyCharm

from django.conf.urls import url
#from .views import *
from .views import user, add_user, del_user, edit_user, set_user_permission, \
clear_user_permission, del_permission, clean_all_privileges, group, del_group, user_add_group,\
user_bind_group, set_group_permission, user_authority_list, set_user_authority, edit_password


urlpatterns = [
    url(r'^user_list/$', user),
    url(r'^add_user/$', add_user),
    url(r'^del_user/$', del_user),
    url(r'^edit_user/$', edit_user),
    url(r'^set_user_permission/$', set_user_permission, name="set_user_p"),
    url(r'^clear_user_permission/$', clear_user_permission, name="uclear"),

    url(r'^edit_password/$', edit_password, name="ed_passwd"),

    url(r'^del_permission', del_permission),
    url(r'^clean_all_privileges', clean_all_privileges),
    url(r'^group/$', group),
    url(r'^del_group/$', del_group, name="dgroup"),
    url(r'^user_add_group/$', user_add_group),
    url(r'^user_bind_group/', user_bind_group, name='gbind'),
    url(r'^set_group_permission/$', set_group_permission, name="set_group_priv"),
    url(r'userAuthority/$', user_authority_list),
    url(r'^set_user_authority', set_user_authority),
]
