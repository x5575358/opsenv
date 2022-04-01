# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from .forms import UserForm
from  opslog.models import LoginRecorder


def login(request):
    context = {}
    if request.method == 'POST':
        form = UserForm(request.POST)
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        if form.is_valid():
            # 获取表单用户密码
            #username = request.POST.get('username', None)
           # password = request.POST.get('password', None)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # 获取的表单数据与数据库进行比较
            user = authenticate(username=username, password=password)
            if user:
                # 比较成功，跳转index
                auth.login(request, user)
                LoginRecorder.objects.create(user_name=username, login_ip=ip, \
                                             login_status=0)
                request.session['username'] = username
                return HttpResponseRedirect(request.POST.get('next', '/index') or '/index')
            else:
                LoginRecorder.objects.create(user_name=username, login_ip=ip, \
                                             login_status=1)
                # 比较失败，还在login
                error = {'error': '<p><font size="2" face="arial" color="red">账号或密码错误.</font></p>'} 
                return render(request, 'login/login.html', error)
        else:
            # 输入空，还在login
            error = {'error': '<p><font size="2" face="arial" color="red">账号和密码不能为空，请重新输入!</font></p>'}
            return render(request, 'login/login.html', error)

    else:
        context = {'isLogin': False, 'pswd': True}
        # return HttpResponse("00000000000")
        return render(request, 'login/login.html', context)


def logout(request):
    # del request.session["username"]  # 删除session
    # uf = UserForm(request.POST)
    auth.logout(request)
    return HttpResponseRedirect("/login/")

