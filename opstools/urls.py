# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/8/31 9:56
# File  : urls.py
# Software PyCharm

from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^tools_list/$', tools_list , name="tools"),
    url(r'^docker_restart/$', docker_restart, name="dockerrestart"),
    url(r'^exce_docker_restart/$', exce_docker_restart, name="excedockerrestart"),
    url(r'^async_result_ret/$', async_result_ret),
    url(r'^read_container_detail/$', read_container_detail, name="opstoolsdetail"),

    url(r'get_hosts_exec_script/$', get_hosts_exec_script, name="gethostsexcescript"),

    url(r'^up_file/$', up_file, name="upfile"),
    url(r'^save_upfiles',save_upfiles, name="savefiles"),
    url(r'^delete_files', delete_files, name="delefiles"),
    url(r'^down_files', down_files, name="downfile"),
    url(r'^cancle_upfiles', cancle_upfiles, name="cancleup"),

    url(r'^script_group_list', script_group_list, name="scriptgroup"),
    url(r'^create_group_script', create_group_script, name="createscriptgroup"),
    url(r'^del_group_info', del_group_info, name="delgroupinfo"),
    url(r'^edit_group_info', edit_group_info, name="editgroupinfo"),

    url(r'^async_exce_script_ret', async_exce_script_ret),

    url(r'^get_script_list_api/', get_script_list_api, name="getscriptlistapi"),
]
