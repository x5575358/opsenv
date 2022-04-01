import json
from user.views import user_privilges_info
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import  HttpResponseRedirect
# from .models import *
from Ops.settings import HARBOR_DOMAIN, HARBOR_PASSWD, HARBOR_NAME 
from api.open_api import bash, dict_add_serial_number
from api.views import log_decor
from .mirror_api import *
from .basic_config import  API_PARAM_LIST



GT = GetDayTime()
TWO_MONTH_AGO = GT.get_pre_later_time(-62, "%Y-%m-%d %H:%M:%S")
NOW_DAY = GT.get_pre_later_time(1, "%Y-%m-%d %H:%M:%S")



@login_required
@permission_required('mirrors.delete_mirrorwarehouse')
def del_mirror(request):
    re_content = {}
    if request.method == "GET":
        req_h = request.GET
        del_id = req_h.get("del_id", "")
        del_mirror_instance(del_id=del_id)
        return HttpResponseRedirect("/mirror/list/")

@login_required
@permission_required('mirrors.scanf_projectinfo')
@log_decor
def project_list(request):
    data = {}
    mirrList = ProjectInfo.objects.all()
    data['data'] = mirrList
    data["exit_priv"] = user_privilges_info(request)
    return render(request, 'mirror/project_list.html', data)

@login_required
@permission_required('mirrors.scanf_warehouse')
@log_decor
def warehouse_list(request):
    data = {}
    warehouses_list = MirrorWarehouse.objects.values('id', 'name', 'tags_count', 'creation_time', \
                      'update_time', 'projecter__name').order_by('-id')
    data['data'] = dict_add_serial_number(warehouses_list)
    data["exit_priv"] = user_privilges_info(request)
    return render(request, 'mirror/warehous_list.html', data)

@login_required
@permission_required('mirrors.scanf_mirrotag')
@log_decor
def tags_list(request):
    data = {}
    tag_list = MirrorTags.objects.values('id', 'name', 'warehouser__name', 'created', 'size', \
              'docker_version').filter(created__range=(TWO_MONTH_AGO, NOW_DAY))
    data['data'] = dict_add_serial_number(tag_list)
    data["exit_priv"] = user_privilges_info(request)
    return render(request, 'mirror/tags_list.html', data)

@login_required
@permission_required('mirrors.change_projectinfo')
@log_decor
def update_project(request):
    harbor_handle = HarborApi(HARBOR_DOMAIN, HARBOR_NAME, HARBOR_PASSWD)
    harbor_handle.login_get_session_id()
    ret = harbor_handle.project_info()
    add_project(ret)
    harbor_handle.logout()
    return HttpResponseRedirect("/mirror/project/")

@login_required
@permission_required('mirrors.change_mirrorwarehouse')
@log_decor
def update_warehouse(request):
    project_id = ProjectInfo.objects.values("id")
    harbor_handle = HarborApi(HARBOR_DOMAIN, HARBOR_NAME, HARBOR_PASSWD)
    for o in project_id:
        harbor_handle.login_get_session_id()
        ret_json = harbor_handle.repository_info(o["id"])
        print("--------update_warehouse----rret_json-------=",ret_json) 
        if len(ret_json) > 0:
            add_warehouse(ret_json)
    harbor_handle.logout()
    return HttpResponseRedirect("/mirror/warehouse/")

@login_required
@permission_required('mirrors.change_mirrortags')
@log_decor
def update_tags(request):
    warehouse_name = MirrorWarehouse.objects.values("id", "name")
    harbor_handle = HarborApi(HARBOR_DOMAIN, HARBOR_NAME, HARBOR_PASSWD)
    for  o in warehouse_name:
        harbor_handle.login_get_session_id()
        ret_json = harbor_handle.tags_info(o["name"])
        if len(ret_json) > 0:
            add_tags(ret_json, o["id"])
    harbor_handle.logout()
    return HttpResponseRedirect("/mirror/tags_list/")
