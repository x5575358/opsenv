"""Ops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
# from django.conf import  settings
# from django.conf.urls.static import static
from django.contrib import admin
from login import views
from .views import *
from .dbinit import tt
# from mirror_image import urls


urlpatterns = [
    url(r'^index', index, name="index"),
    url(r'^accounts/login/', views.login),
    url(r'^login', views.login),
    url(r'^logout', views.logout),
    url(r'^mirror/', include('mirrors.urls', namespace="mirror")),
    url(r'^user/', include('user.urls', namespace="ouser")),
    url(r'^container/', include('opscontainer.urls', namespace="opscont")),

    url(r'^log/', include('opslog.urls', namespace="log")),
    url(r'^asset/', include('asset.urls', namespace="asset")),
    url(r'^release/', include('release.urls', namespace="in_release")),

    url(r'^dbinit/$', tt),
    url(r'^$', views.login),
    url(r'^mchange/', include('mchange.urls', namespace="mchange")),
    url(r'^opstools/', include('opstools.urls', namespace="opstools")),
    url(r'^continuousd/', include('continuous_deployment.urls', namespace="cdeployment")),
]
