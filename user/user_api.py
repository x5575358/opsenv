# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/7/16 16:11
# File  : api.py
# Software PyCharm

from django.contrib.auth.models import User, Group
from django.db.models import Q

def id_codename_dict(src):
    ret_dict={}
    for o in  src:
        ret_dict.update({o["codename"]:o["id"]})
    return ret_dict

def exit_privileges_codename(src):
    ret_list = []
    for  o  in src:
        ret_list.append(o["codename"])
    return ret_list

def get_group_user_list():
    user_src_list = User.objects.all().filter(~Q(username='admin'))
    user_list = []
    group_user_list = []
    for u in user_src_list:
        if not User.objects.get(username=u).groups.exists():
            user_list.append(u)
        else:
            group_user_list.append(u)
    return user_list,group_user_list

def get_group_user(gid):
    user_src_list = User.objects.all().filter(~Q(username='admin'))
    group_user_list = []
    user_list = []
    for u in user_src_list:
        if  User.objects.get(username=u).groups.exists():
            exit_gid = User.objects.get(username=u).groups.values("id","name")[0]["id"]
            if int(gid) == exit_gid:
                group_user_list.append(u)
        else:
            user_list.append(u)
    return user_list,group_user_list
