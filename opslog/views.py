from django.shortcuts import render

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required,permission_required
# Create your views here.
import datetime
from datetime import timedelta
from .log_api import execlog_log_list, ExecLog
from api.models import AsyncOperationAudit
from opstools.models import AsyncFileInfo, ScriptGroupRelease
from api.open_api import read_file
from api.views import log_decor
from release.views import code_trans_lang
from mirrors.mirror_api import GetDayTime
from opslog.models import LoginRecorder
from user.views import user_privilges_info


GT = GetDayTime()
SERVEN_DAY_AGO = GT.get_pre_later_time(-7, "%d/%m/%Y")
NOW_DAY = GT.get_pre_later_time(0, "%d/%m/%Y")
SEARCH_SERVEN_DAY_AGO = GT.get_pre_later_time(-7, "%Y-%m-%d")
SEARCH_NOW_DAY = GT.get_pre_later_time(1, "%Y-%m-%d")

@login_required
@permission_required('opslog.scanf_log')
@log_decor
def loglist(request):
    data={}
    if request.method == "GET":
        data["start_time"] = SERVEN_DAY_AGO
        data["end_time"] = NOW_DAY
        data["exit_priv"] = user_privilges_info(request)
        obj = ExecLog.objects.filter(create_time__range=(SEARCH_SERVEN_DAY_AGO, \
                       SEARCH_NOW_DAY)).values("id", "user", "cmd", "remote_ip", \
                       "log_level", "create_time").order_by("-id")
        data['data'] = code_trans_lang(obj)
        return  render(request, "opslog/log_list.html", data)
    else:
        req_handle = request.POST
        get_st_time = req_handle["st_time"]
        get_ed_time = req_handle["ed_time"]
        st_time_list = get_st_time.split("/")[::-1]
        ed_time_list = get_ed_time.split("/")[::-1]
        st_time_int = int(",".join(st_time_list).replace(",",""))
        ed_time_int = int(",".join(ed_time_list).replace(",",""))
        st_time = datetime.datetime.strptime(','.join(st_time_list).replace(",","-"),"%Y-%m-%d")
        ed_time = datetime.datetime.strptime(','.join(ed_time_list).replace(",","-"),"%Y-%m-%d")
        if st_time_int - ed_time_int > 0:
            data["error_info"] = "<h5 style=\"color:red\">起始时间大于终止时间，请重新选择!</h5>"
        data["start_time"] = get_st_time
        data["end_time"] = get_ed_time
        data["exit_priv"] = user_privilges_info(request)
        obj = ExecLog.objects.filter(create_time__range=(st_time, ed_time + timedelta(days=1))).values("id", \
                       "user", "cmd", "remote_ip", "log_level", "create_time").order_by("-id")
        data['data'] = code_trans_lang(obj)
        return  render(request,"opslog/log_list.html",data)

@login_required
@permission_required('opslog.scanf_log')
@log_decor
def async_log_list(request):
    data={}
    if request.method == "GET":
        data["start_time"] = SERVEN_DAY_AGO
        data["end_time"] = NOW_DAY
        print(SEARCH_SERVEN_DAY_AGO, SEARCH_NOW_DAY)
        obj = AsyncOperationAudit.objects.filter(creation_time__range=(\
                       SEARCH_SERVEN_DAY_AGO, SEARCH_NOW_DAY)).values("id", "exce_order", \
                       "release_status", "user", "creation_time", "remote_ip").order_by("-id")
        data["data"] = code_trans_lang(obj)
        data["exit_priv"]=user_privilges_info(request)
        return  render(request, "opslog/async_log_list.html", data)
    else:
        req_handle = request.POST
        get_st_time = req_handle["st_time"]
        get_ed_time = req_handle["ed_time"]
        st_time_list = get_st_time.split("/")[::-1]
        ed_time_list = get_ed_time.split("/")[::-1]
        st_time_int = int(",".join(st_time_list).replace(",",""))
        ed_time_int = int(",".join(ed_time_list).replace(",",""))
        st_time = datetime.datetime.strptime(','.join(st_time_list).replace(",","-"),"%Y-%m-%d")
        ed_time = datetime.datetime.strptime(','.join(ed_time_list).replace(",","-"),"%Y-%m-%d")
        if st_time_int - ed_time_int > 0:
            data["error_info"] = "<h5 style=\"color:red\">起始时间大于终止时间，请重新选择!</h5>"
        data["start_time"] = get_st_time
        data["end_time"] = get_ed_time
        data["exit_priv"] = user_privilges_info(request)
        obj = AsyncOperationAudit.objects.filter(creation_time__range=(\
                       st_time, ed_time + timedelta(days=1))).values("id", "exce_order", "release_status", \
                       "user", "creation_time", "remote_ip").order_by("-id")
        data["data"] = code_trans_lang(obj)
        return  render(request, "opslog/async_log_list.html", data)
    

@login_required
@permission_required('opslog.scanf_log')
@log_decor
def sacnf_async_log(request):
    if request.method == "GET":
        data={}
        id = request.GET.get("id")
        file_path=AsyncOperationAudit.objects.filter(id=id).values("file_path","exce_order",\
                                                    "user","creation_time","remote_ip")
        data["exce_order"]=file_path[0]["exce_order"]
        data["user"]=file_path[0]["user"]
        data["remote_ip"] = file_path[0]["remote_ip"]
        data["creation_time"] = file_path[0]["creation_time"]
        f_content = read_file(file_path[0]["file_path"])
        data["f_content"] = f_content
        data["exit_priv"]=user_privilges_info(request)
        return render(request, "opslog/scanf_async_log_detail.html", data)

@login_required
@permission_required('opslog.scanf_log')
@log_decor
def login_log_list(request):
    data = {}
    if request.method == "GET":
        data["start_time"] = SERVEN_DAY_AGO
        data["end_time"] = NOW_DAY
        obj = LoginRecorder.objects.filter(creation_time__range=(SEARCH_SERVEN_DAY_AGO, \
                       SEARCH_NOW_DAY)).values("id", "user_name", "login_ip", "creation_time", \
                      "login_status").order_by("-creation_time")
        data["data"] = code_trans_lang(obj)
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opslog/login_log_list.html", data)
    else:
        req_handle = request.POST
        get_st_time = req_handle["st_time"]
        get_ed_time = req_handle["ed_time"]
        st_time_list = get_st_time.split("/")[::-1]
        ed_time_list = get_ed_time.split("/")[::-1]
        st_time_int = int(",".join(st_time_list).replace(",",""))
        ed_time_int = int(",".join(ed_time_list).replace(",",""))
        st_time = datetime.datetime.strptime(','.join(st_time_list).replace(",","-"),"%Y-%m-%d")
        ed_time = datetime.datetime.strptime(','.join(ed_time_list).replace(",","-"),"%Y-%m-%d")
        if st_time_int - ed_time_int > 0:
            data["error_info"] = "<h5 style=\"color:red\">起始时间大于终止时间，请重新选择!</h5>"
        data["start_time"] = get_st_time
        data["end_time"] = get_ed_time
        data["exit_priv"] = user_privilges_info(request)
        obj = LoginRecorder.objects.filter(creation_time__range=(st_time, ed_time + timedelta(days=1))).values("id", \
                        "user_name", "login_ip", "creation_time", "login_status").order_by("-creation_time")
        data["data"] = code_trans_lang(obj)
        return render(request, "opslog/login_log_list.html", data)

@login_required
@permission_required('opstools.scanf_asyncfileinfo')
@log_decor
def restart_tools_log(request):
    data = {}
    if request.method == "GET":
        data["start_time"] = SERVEN_DAY_AGO
        data["end_time"] = NOW_DAY
        async_info = AsyncFileInfo.objects.filter(create_time__range=(SEARCH_SERVEN_DAY_AGO, \
                       SEARCH_NOW_DAY )).values("id", "req_user", "hosts_name", "create_tags", \
                     "excute_status", "create_time", "update_time").order_by("-create_time")
        data["data"] = code_trans_lang(async_info)
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opslog/restart_log_list.html", data)
    else:
        req_handle = request.POST
        get_st_time = req_handle["st_time"]
        get_ed_time = req_handle["ed_time"]
        st_time_list = get_st_time.split("/")[::-1]
        ed_time_list = get_ed_time.split("/")[::-1]
        st_time_int = int(",".join(st_time_list).replace(",",""))
        ed_time_int = int(",".join(ed_time_list).replace(",",""))
        st_time = datetime.datetime.strptime(','.join(st_time_list).replace(",","-"),"%Y-%m-%d")
        ed_time = datetime.datetime.strptime(','.join(ed_time_list).replace(",","-"),"%Y-%m-%d")
        if st_time_int - ed_time_int > 0:
            data["error_info"] = "<h5 style=\"color:red\">起始时间大于终止时间，请重新选择!</h5>"
        data["start_time"] = get_st_time
        data["end_time"] = get_ed_time
        data["exit_priv"] = user_privilges_info(request)
        async_info = AsyncFileInfo.objects.filter(create_time__range=(st_time, \
                       ed_time + timedelta(days=1))).values("id", "req_user", "hosts_name", "create_tags", \
                     "excute_status", "create_time", "update_time").order_by("-create_time")
        data["data"] =code_trans_lang(async_info)
        return render(request, "opslog/restart_log_list.html", data)

@login_required
@permission_required('opstools.scanf_scriptgrouprelease')
@log_decor
def exec_script_group(request):
    data = {}
    if request.method == "GET":
        data["start_time"] = SERVEN_DAY_AGO
        data["end_time"] = NOW_DAY
        obj = ScriptGroupRelease.objects.filter(create_time__range=(SEARCH_SERVEN_DAY_AGO, \
                       SEARCH_NOW_DAY)).values("group_uniqu_tag","relate_script_group__title_name", "hosts_ip", \
                       "hosts_name", "operator_user", "release_status", "create_time", \
                       "update_time").order_by("-create_time")
        data["data"] = code_trans_lang(obj)
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opslog/tool_exce_script_log.html", data)
    else:
        req_handle = request.POST
        get_st_time = req_handle["st_time"]
        get_ed_time = req_handle["ed_time"]
        st_time_list = get_st_time.split("/")[::-1]
        ed_time_list = get_ed_time.split("/")[::-1]
        st_time_int = int(",".join(st_time_list).replace(",",""))
        ed_time_int = int(",".join(ed_time_list).replace(",",""))
        st_time = datetime.datetime.strptime(','.join(st_time_list).replace(",","-"),"%Y-%m-%d")
        ed_time = datetime.datetime.strptime(','.join(ed_time_list).replace(",","-"),"%Y-%m-%d")
        if st_time_int - ed_time_int > 0:
            data["error_info"] = "<h5 style=\"color:red\">起始时间大于终止时间，请重新选择!</h5>"
        data["start_time"] = get_st_time
        data["end_time"] = get_ed_time
        print("----------get_st_time-----------", get_st_time)
        data["exit_priv"] = user_privilges_info(request)
        obj = ScriptGroupRelease.objects.filter(create_time__range=(st_time, \
                       ed_time + timedelta(days=1))).values("relate_script_group__title_name", "hosts_ip", \
                       "hosts_name", "operator_user", "release_status", "create_time", \
                       "update_time", "log_path").order_by("-create_time")
        data["data"] = code_trans_lang(obj)
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opslog/tool_exce_script_log.html", data)
