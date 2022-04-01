# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/12 16:33
# File  : urls.py
# Software PyCharm

from django.conf.urls import url
#from .views import *
from .views import task_list, history_task_list, hosts_list, add_hosts, add_task, del_task, \
edit_task, check_network, exec_task, load_exce_data, scanf_exce_detail, get_difference_container, \
update_difference_container, exec_synchronization_container, constrast_check_network, \
cancel_check_network, del_hosts, after_constrat_add_task, constrast_new_add_check_network


urlpatterns = [
    url(r'^task_list/$', task_list, name="task_list"),
    url(r'^history_task_list/$', history_task_list),
    url(r'^hosts_list/$', hosts_list, name="hostslist"),

    url(r'^add_hosts/$', add_hosts, name="addhosts"),
    url(r'^del_hosts/$', del_hosts, name="delhosts"),
    url(r'^add_task/$', add_task, name="addtask"),
    url(r'^after_constrat_add_task/$', after_constrat_add_task, name="constrataddtask"),

    url(r'^del_task/', del_task),
    url(r'^edit_task/', edit_task),

    url(r'^check_network/', check_network),
    url(r'^exec_task/', exec_task),
    url(r'^load_exce_data/', load_exce_data),

    url(r'^scanf_exce_detail/', scanf_exce_detail),

    url(r'^get_difference_container/$', get_difference_container, name="diff_container"),
    url(r'^update_difference_container/$', update_difference_container, name="updatediff"),
    url(r'^exec_synchronization_container/$', exec_synchronization_container, name="exce_sync"),
    url(r'^constrast_check_network/$', constrast_check_network, name="check_network"),
    url(r'^cancel_check_network/$', cancel_check_network),

    url(r'^constrast_new_add_check_network/$', constrast_new_add_check_network, name="add_check_network"),
]
