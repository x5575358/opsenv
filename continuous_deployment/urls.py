# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/7/3 13:38
# File  : urls.py
# Software PyCharm


from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^gitlab_commit_api/$', gitlab_commit_api, name="gitlabcommit"),
    url(r'^gitlab_commit_list/$', gitlab_commit_list, name="gitlabrecord"),
    url(r'^build_over_alert/$', build_over_alert, name="buildalert"),
    url(r'^jenkins_build_list/$', jenkins_build_list, name="buildlist"),
    url(r'^jenkins_build_detail/$', jenkins_build_detail, name="builddetail"),
    url(r'^jenkins_sucessful_list/$', jenkins_build_sucessful_list, name="buildsucess"),
    url(r'^retry_run_pipeline/$', retry_run_pipeline, name="retrypipeline"),

    url(r'^config_commit_api/$', gitlab_config_commit_api, name="gitlabconfigcommit"),
    url(r'^config_commit_list/$', gitlab_config_commit, name="gitlabconfigrecord"),
]
