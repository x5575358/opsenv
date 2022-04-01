# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import  datetime
from django.shortcuts import render, render_to_response
# from work import models
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission
from django.contrib.auth import authenticate
from django.db.models import Q
from django.contrib import auth
from login.forms import UserForm
from opslog.log_api import  logger, create_execLog, request_client_ip
from .user_api import id_codename_dict, exit_privileges_codename, get_group_user_list, \
get_group_user
from Ops.settings import UCREATE_USER_MODEL 
from api.views import send_mail_msg, log_decor

@login_required
@permission_required('auth.scanf_user')
@log_decor
def user(request):
    data = {}
    obj = User.objects.values("id", "username", "is_superuser", "is_active", "is_staff", "email", \
          "first_name", "last_login").filter(~Q(username='admin'))
    data['data'] = obj
    print(obj)
    data["exit_priv"] = user_privilges_info(request)
    print(data["exit_priv"])
    return render(request, 'user/user_list1.html', data)

@login_required
@permission_required('auth.delete_user')
@log_decor
def del_user(request):
    del_id = request.GET.get('del_id')
    del_user = request.GET["del_username"]
    ex_cmd = str(request.user)+" removed the user %s account "%del_user
    create_execLog(user=request.user, host="", remote_ip=request_client_ip(request), cmd=ex_cmd, \
                   result=0, op_time=datetime.datetime.now())
    logger.debug(ex_cmd)
    User.objects.get(id=del_id).user_permissions.clear()
    User.objects.filter(id=del_id).delete()
    return HttpResponseRedirect('/user/user_list/')

@login_required
@log_decor
def edit_password(request):
    data = {}
    if request.method == 'POST':
            password = request.POST.get('password')
            s_password = request.POST.get('s_password')
            username = request.user
            if password == s_password:
                user = User.objects.get(username=username)
                if user is not None and user.is_active:
                    user.set_password(password)
                    user.save()
                    return HttpResponseRedirect('/login/')
            else:
                data["userExit"]="两次输入密码不相同，请重新输入!"
                data["exit_priv"] = user_privilges_info(request)
                return render(request, 'user/edit_password.html', data)
    else:
        data = {'isLogin': False}
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'user/edit_password.html', data)

@login_required
@permission_required('auth.add_user')
@log_decor
def add_user(request):
    remote_ip = request_client_ip(request)
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if User.objects.filter(username=username):
                context['userExit'] = '用户名已经存在'
                ex_cmd = str(request.user) + " add the user %s account Failed,because the user is \
                         exit " % username
                logger.debug(ex_cmd)
                create_execLog(user=request.user, host="", remote_ip=remote_ip, cmd=ex_cmd, \
                               result=0, op_time=datetime.datetime.now())
                return render(request, 'user/add_user.html', context)
            email = request.POST.get('email')
            is_active = request.POST.get('is_active')
            is_staff = request.POST.get('is_staff')
            is_superuser = request.POST.get('is_superuser')
            nickname =  request.POST.get('nickname')
            User.objects.create_user(username=username, password=password, first_name = nickname, \
                 is_superuser=is_superuser, email=email, is_active=is_active, is_staff=is_staff)
            ex_cmd = str(request.user) + " add the user %s account sucessful " % username
            logger.debug(ex_cmd)
            create_execLog(user=request.user, host="", remote_ip=remote_ip, cmd=ex_cmd, \
                           result=0, op_time=datetime.datetime.now())
            msg = UCREATE_USER_MODEL%(username, username, password)
            send_mail_msg(email, "用户新增", msg)
            return HttpResponseRedirect('/user/user_list/')
    else:
        data = {}
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'user/add_user.html', data)


@login_required
@permission_required('auth.add_permission')
@log_decor
def set_user_permission(request):
    data = {}
    username = request.GET.get('username')
    if request.method == 'POST':
        permission_namecode = request.POST.getlist("permission[]")
        usern = request.POST.get("usern")
        pre_values = Permission.objects.values("id", "codename")
        pre_dict = id_codename_dict(pre_values)
        User.objects.get(username=usern).user_permissions.clear()
        for per in permission_namecode:
            User.objects.get(username=usern).user_permissions.add(pre_dict[per])
        return JsonResponse({"msg":"200", "url":"/user/user_list/"})
    else:
        data['data'] = Permission.objects.values()
        src_codename = User.objects.get(username=username).user_permissions.values("codename")
        exit_group_priv = exit_privileges_codename(src_codename)
        if User.objects.get(username=username).groups.exists():
            user_group_id = User.objects.get(username=username).groups.values("id")
            for  gid in user_group_id:
                g_priv = Group.objects.get(id=gid["id"]).permissions.values("codename")
                g_priv_list = exit_privileges_codename(g_priv)
                exit_group_priv = exit_group_priv + g_priv_list
        data['exit_group_priv'] = exit_group_priv
        data["exit_priv"] = user_privilges_info(request)
        data['username'] = username
        return render(request, 'user/set_user_permission.html', data)

@login_required
@permission_required('auth.change_user')
@log_decor
def edit_user(request):
    i = request.POST.get
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            is_active = request.POST.get('is_active')
            is_staff = request.POST.get('is_staff')
            email = request.POST.get('email')
            is_superuser = request.POST.get('is_superuser')
            if password and password not in "******":
                User.objects.filter(username=username).update(is_active=is_active, \
                     is_superuser=is_superuser, is_staff=is_staff, email=email)
                user = User.objects.get(username=username)
                if user is not None and user.is_active:
                    user.set_password(password)
                    user.save()
                    return HttpResponseRedirect('/user/user_list/')
            else:
                User.objects.filter(username=username).update(is_active=is_active, \
                     is_superuser=is_superuser, is_staff=is_staff, email=email)
                return HttpResponseRedirect('/user/user_list/')
    else:
        data = {}
        username = request.GET.get("edit_username")
        data["data"] = User.objects.filter(username=username).values()
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'user/edit_user.html', data)


@login_required
@permission_required('auth.scanf_group')
@log_decor
def group(request):
    data = {}
    obj = Group.objects.all()
    data['data'] = obj
    data["exit_priv"] = user_privilges_info(request)
    return render(request, 'user/group_list.html', data)

@login_required
@permission_required('auth.delete_group')
@log_decor
def del_group(request):
    if  request.method == 'GET':
        del_id = request.GET.get('del_id')
        Group.objects.filter(id=del_id).delete()
        return HttpResponseRedirect('/user/group/')

@login_required
@log_decor
def group_set_permission(request):
    data = {}
    group_name = request.GET.get('group_name')
    if request.method == 'POST':
        i = request.POST.get
        permission_id = i('permission_id')
        print(permission_id)
        Group.objects.get(name=group_name).permissions.add(permission_id)
        return HttpResponseRedirect('/users')
    else:
        data = {}
        data['data'] = Permission.objects.values()
        data['username'] = group_name
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'users/set_permission.html', data)
    # id = request.GET.get('id')
    # data['data'] = Group.objects.get(id=id).permissions.values()
    # return render(request, 'users/group.html', data)

@login_required
def user_authority_list(request):
    data = {}
    data['data'] = Permission.objects.values()
    data["exit_priv"] = user_privilges_info(request)
    return render(request, 'user/user_authority_list.html', data)

@login_required
@log_decor
def set_user_authority(request):
    data = {}
    username = request.GET.get('username')
    print(username)
    if request.method == 'POST':
        permission_ids = request.POST.getlist('permission_id[]')
        print(permission_ids)
        for permission_id in permission_ids:
            User.objects.get(username=username).user_permissions.add(permission_id)
        return HttpResponseRedirect('/user/set_user_authority/')
    else:
        data['data'] = Permission.objects.values()
        data['exit_data'] = User.objects.get(username=username).user_permissions.values()
        return HttpResponse("wwwwwwww")
        data['username'] = username
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'user/set_user_authority.html', data)

@login_required
@permission_required('auth.delete_permission')
def del_permission(request):
    data = {}
    username = request.GET.get('username')
    if request.method == 'POST':
        i = request.POST.get
        permission_ids = request.POST.getlist('permission_id[]')
        for permission_id in permission_ids:
            User.objects.get(username=username).user_permissions.remove(permission_id)
        return HttpResponseRedirect('/user/user_list/')
    else:
        data['data'] = User.objects.get(username=username).user_permissions.values()
        data['username'] = username
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'user/del_permission.html', data)


@login_required
@permission_required('auth.delete_permission')
def clean_all_privileges(request):
    username = request.GET.get('username')
    clear = request.GET.get('clean_all_privileges')
    if clear:
        User.objects.get(username=username).user_permissions.clear()
    return HttpResponseRedirect('/user/user_list/')



@login_required
@permission_required('auth.add_group')
@log_decor
def user_add_group(request):
    data = {}
    if request.method == 'POST':
        groupname = request.POST.get('groupname')
        Group.objects.create(name=groupname)
        return HttpResponseRedirect('/user/group/')
    else:
        data['userinfo'] = User.objects.all()
        data['permiss'] = Permission.objects.values()
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'user/add_group.html', data)

@login_required
@permission_required('auth.add_permission')
@log_decor
def set_group_permission(request):
    group_name = request.GET.get('name')
    if request.method == 'POST':
        permission_namecode = request.POST.getlist("permission[]")
        usern = request.POST.get("usern")
        pre_values = Permission.objects.values("id", "codename")
        pre_dict = id_codename_dict(pre_values)
        Group.objects.get(name=usern).permissions.clear()
        for per in permission_namecode:
            Group.objects.get(name=usern).permissions.add(pre_dict[per])
        return JsonResponse({"msg": "200", "url": "/user/group/"})
    else:
        data = {}
        data['data'] = Permission.objects.values()
        data['username'] = group_name
        src_codename = Group.objects.get(name=group_name).permissions.values("codename")
        exit_group_priv = exit_privileges_codename(src_codename)
        data['exit_group_priv'] = exit_group_priv
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'user/set_group_permission.html', data)

@login_required
@permission_required('auth.add_permission')
@log_decor
def user_bind_group(request):
    data = {}
    username = request.GET.get('name')
    if request.method == 'POST':
        user = request.POST.getlist('user')
        groups = request.POST.get('groupname')
        groups_id = Group.objects.get(name=groups)
        if len(user) == 0:
            user_list, group_user_list = get_group_user_list()
            for gu in group_user_list:
                if User.objects.get(username=gu).groups.exists():
                    User.objects.get(username=gu).groups.remove(groups_id)
        for u in user:
            if not User.objects.get(username=u).groups.exists():
                User.objects.get(username=u).groups.add(groups_id)
                # 解除u用户对应的所有组
                # User.objects.get(username=u).groups.clear()
                #解除u用户对应的groups_id组
                # User.objects.get(username=u).groups.remove(groups_id)
        return HttpResponseRedirect('/user/group/')
    else:
        gid = request.GET.get('id')
        data["ganme"] = Group.objects.filter(id=gid).values("name")[0]["name"]
        user_list, group_user_list = get_group_user(gid) 
        data["exit_priv"] = user_privilges_info(request)
        data["user_list"] = user_list
        data["group_user_list"] = group_user_list
        return render(request, 'user/user_bind_group.html', data)

@login_required
def user_privilges_info(request):
    user = request.user
    # print("role------------",User.objects.filter(username=user).values("role"))
    priv_dict = {}
    exit_group_priv = []
    user_group_id = User.objects.get(username=user).groups.values("id")
    for  gid in user_group_id:
        g_priv = Group.objects.get(id=gid["id"]).permissions.values("codename")
        g_priv_list = exit_privileges_codename(g_priv)
        exit_group_priv = exit_group_priv + g_priv_list
    mid_priv = User.objects.get(username=user).user_permissions.values()
    for  i  in mid_priv:
        priv_dict.update({i["codename"]:"0"})
    for o in exit_group_priv:
        priv_dict.update({o:"0"})
    return priv_dict

@login_required
@permission_required('auth.delete_permission')
@log_decor
def clear_user_permission(request):
    if  request.method == "GET":
        uname = request.GET["username"]
        User.objects.get(username=uname).user_permissions.clear()
        user_group_id = User.objects.get(username=uname).groups.values("id")
        for  gid in user_group_id:
            User.objects.get(username=uname).groups.remove(gid["id"])
        return HttpResponseRedirect('/user/user_list/')
