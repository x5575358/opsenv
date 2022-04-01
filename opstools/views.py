from django.shortcuts import render, redirect, reverse, HttpResponseRedirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Count
# Create your views here.
import os
import time
import json
import random
import datetime
from api.views import log_decor
from release.models import HostsInfo
from release.views import code_trans_lang
from release.release_api import DockerRemoteApi
from mirrors.mirror_api import GetDayTime
from Ops.settings import CONTAINER_RESTART_DIR, UPFILE_PATH, ANSY_RET_DIR
from user.views import user_privilges_info
from api.open_api import bash, write_file, async_restart_container, read_file
from .opstools_api import async_exec_script_group, auto_create_exce_group_script
from .api import async_docker_restart
from .models import RunContainer, AsyncFileInfo, UploadFiles, ScriptGroup, \
ScriptGroupRelease, ScriptGroupExecSeq

@login_required
@log_decor
@permission_required('opstools.scanf_runcontainer')
def tools_list(request):
    data = {}
    if request.method == 'GET':
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opstools/tools_list.html",data)

@login_required
@permission_required('opstools.add_runcontainer')
def docker_restart(request):
    data = {}
    if request.method == 'POST':
        req_handle = request.POST
        name_ip_list = req_handle.getlist("ips")
        container_list = []
        docker_handle = DockerRemoteApi()
        RunContainer.objects.filter(excute_status=3).delete()
        for name_ip in name_ip_list:
            mid_list = name_ip.split(":")
            name = mid_list[0]
            ip = mid_list[1]
#            bash_order = "ansible %s -m command -a \"docker ps\"|awk -F \" \" '{print  $2}'|\
#                         grep  -v \"ID\"|grep -v \"|\""%(name)
#            print("------list_values-----", bash_order)
#            values_str = bash(bash_order)
#            list_values = values_str.split("\n")[:-1]
            list_values = docker_handle.docker_ps_list(ip, "dict")
            print("------list_values-----", list_values,"-----type(list_values)----",type(list_values))
            tags = str(time.time())
            for key,value in list_values.items():
                print("------value-----", value)
                RunContainer.objects.create(create_tags=tags, hosts_name=name, \
                                            hosts_ip=ip, container_name=key, container_id=value)
            data["tags"]=tags
            mid_dict = RunContainer.objects.filter(create_tags=tags).values("id", \
                         "hosts_name", "container_name")
            print("-------mid_dict-----",mid_dict)
            container_list = container_list + list(mid_dict)
        data["data"] = container_list
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opstools/get_run_container.html", data)
    else:
        ips = HostsInfo.objects.values("id", "ip", "name")
        data["ips"]=ips
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opstools/docker_restart.html", data)

@login_required
@log_decor
@permission_required('opstools.add_runcontainer')
def exce_docker_restart(request):
    data = {}
    if request.method == 'POST':
        req_handle = request.POST
        exce_id = req_handle["exce_id"]
        exce_id_list = json.loads(exce_id)
        hosts_ip_list = RunContainer.objects.filter(excute_status=3).values("hosts_ip", "hosts_name", "create_tags").distinct()
        mid_list = []
        print("--exce_id-------",exce_id)
        for ids in range(len(exce_id_list)):
            mid_value = RunContainer.objects.filter(id=exce_id_list[ids]).values("hosts_ip", "hosts_name", "container_name", "container_id")
            if mid_value:
                mid_list.append(mid_value[0])
        print("-----hosts_ip_list----",hosts_ip_list)
        restart_info_dict = {}
        for hosts in hosts_ip_list:
            file_value_list = []
            print("----hosts------",hosts)
            print("----mid_list------",mid_list)
            for value in mid_list:
                if hosts["hosts_ip"] == value["hosts_ip"]:
                    file_value_list.append(value["container_id"])
            if file_value_list:
                restart_info_dict.update({hosts["hosts_ip"]:file_value_list})
                AsyncFileInfo.objects.create(create_tags=hosts["create_tags"], hosts_name=hosts["hosts_name"], \
                              excute_status=0, req_user=request.user)

        async_docker_restart.delay(restart_info_dict)
        data["exit_priv"] = user_privilges_info(request)
        return HttpResponse(json.dumps({"data":"/log/tools_restart_log/"}), content_type="application/json")

@log_decor
def async_result_ret(request):
    data = {}
    if request.method == 'POST':
        req_handle = request.POST
        file_name = req_handle.get("filename","")
        ret_status = req_handle.get("ret_status","0")
        NOW_TIME = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("-----file_name------",file_name)
        print("-----file_name111------",AsyncFileInfo.objects.filter(file_name=file_name).values("excute_status"))
        if AsyncFileInfo.objects.filter(file_name=file_name).values("excute_status"):
            AsyncFileInfo.objects.filter(file_name=file_name).update(excute_status=ret_status, update_time=NOW_TIME)
            return JsonResponse({"ret": "sucessful"}, status=200)
        return JsonResponse({"ret": "false"}, status=401)

@login_required
def read_container_detail(request):
    if request.method == "POST":
        req_handle = request.POST
        tags = req_handle["create_tags"].replace("\"","")
        obj = RunContainer.objects.filter(create_tags=tags).filter(~Q(excute_status=3)).values("container_name")
        container_list = []
        for mid_var in obj:
            container_list.append(mid_var["container_name"])
        container_str = ','.join(container_list).replace(",", "<br>")
        return JsonResponse({"data": container_str}, status=200)


@login_required
@log_decor
@permission_required('opstools.scanf_uploadfiles')
def up_file(request):
    data = {}
    if request.method == 'POST':
        obj = request.FILES.getlist("upload")
        c_user = request.user
        file_name_list = []
        file_tags = int(str(time.time()).replace(".",""))
        for mid_obj in obj:
            file_name_list.append(mid_obj.name)
            up_file_size = round(mid_obj.size/1024/1024,4)
            if mid_obj.name.endswith(".py") or mid_obj.name.endswith(".sh"):
                files_dir = os.path.join(UPFILE_PATH, 'script')
            elif mid_obj.name.endswith(".jpg") or mid_obj.name.endswith(".png"):
                files_dir = os.path.join(UPFILE_PATH, 'img')
            else:
                files_dir = os.path.join(UPFILE_PATH, 'other')
            if not os.path.exists(files_dir):
                os.mkdir(files_dir)
            files_path = os.path.join(files_dir, mid_obj.name)
            if not os.path.exists(files_path):
                f = open(files_path, 'wb')
                for chunk in mid_obj.chunks():
                    f.write(chunk)
                f.close()
                dest_size = round(os.path.getsize(files_path)/1024/1024,4)
                if up_file_size ==  dest_size:
                    UploadFiles.objects.create(up_user=c_user, file_name=mid_obj.name, \
                                file_save_path=files_path, file_size=dest_size, up_tags=file_tags)
                else:
                    UploadFiles.objects.filter(file_save_path=files_path).delete()
                    os.remove(files_path)
                    data["error_tags"] = "<h5 style=\"color: red;\">%s文件\
                上传失败。<br></h5>"%mid_obj.name
                data["success_tags"] = "<h5 style=\"color: red;\">文件\
                上传成功。<br></h5>"
                data["data"] = UploadFiles.objects.filter(up_tags=file_tags).values("file_name")
                print("---------upfile--------------",UploadFiles.objects.filter(up_tags=file_tags).values("up_tags"))
                data["up_tags"] = UploadFiles.objects.filter(up_tags=file_tags).values("up_tags")[0]["up_tags"]
                print("------------data---------", data)
            else:
                data["data"] = UploadFiles.objects.all().values("id", "up_user", "file_name", \
                    "file_size", "create_time", "remarks", "file_save_path").order_by("-id")
                data["error_tags"] = "<h5 style=\"color: red;\">%s文件\
                已存在，不允许重复上传。<br></h5>"%mid_obj.name
                data["exit_priv"] = user_privilges_info(request)
                return render(request, 'opstools/upload_file_list.html', data)
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'opstools/save_upfiles.html', data)
    else:
        data["data"] = UploadFiles.objects.all().values("id", "up_user", "file_name", \
                    "file_size", "create_time", "remarks", "file_save_path").order_by("-id")
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'opstools/upload_file_list.html', data)

@login_required
@permission_required('opstools.add_uploadfiles')
@log_decor
def save_upfiles(request):
    if request.method == 'POST':
        req_handle = request.POST
        save_tags = req_handle["up_tags"]
        save_remarks = req_handle["sav_remarks"]
        UploadFiles.objects.filter(up_tags=save_tags).update(remarks=save_remarks)
        return HttpResponseRedirect(reverse('opstools:upfile'))

@login_required
@permission_required('opstools.scanf_scriptgroup')
@log_decor
def script_group_list(request):
    data = {}
    if request.method == 'GET':
        obj = ScriptGroup.objects.values("id", "title_name", "create_user", \
              "relate_id__file_name", "create_time", "update_time", "group_uniqu_tag")
        obj_count = ScriptGroup.objects.values("create_user", \
                    "group_uniqu_tag", "title_name").annotate(times=Count("group_uniqu_tag"))
        script_seq = ScriptGroupExecSeq.objects.values("script_exce_order", "script_group_tag")
        script_seq_obj = []
        for tran_var in script_seq:
            script_seq_obj.append(dict({"script_exce_order":json.loads(tran_var["script_exce_order"]), \
                            "script_group_tag":tran_var["script_group_tag"]}))
        data["script_seq"] = script_seq_obj
        single_tags_list = []
        mid_list = []
        for single_nu in obj:
            tmp_list = []
            single_tags_dict = {}
            if not single_tags_list:
                single_tags_dict.update({"id":single_nu["id"]})
                single_tags_dict.update({"tag": single_nu["group_uniqu_tag"]})
                single_tags_list.append(single_tags_dict)
                mid_list.append(single_nu["group_uniqu_tag"])
            if single_nu["group_uniqu_tag"] not in mid_list:
                single_tags_dict.update({"id":single_nu["id"]})
                single_tags_dict.update({"tag": single_nu["group_uniqu_tag"]})
                mid_list.append(single_nu["group_uniqu_tag"])
                single_tags_list.append(single_tags_dict)
        data["single_tags_list"] = single_tags_list
        data["obj_count"] = obj_count
        data["obj"] = obj
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opstools/script_group_list.html", data)


@login_required
@log_decor
def cancle_upfiles(request):
    if request.method == 'GET':
        cancle_id = request.GET["tags"]
        UploadFiles.objects.filter(up_tags=cancle_id).delete()
        return HttpResponseRedirect(reverse('opstools:upfile'))

@login_required
@permission_required('opstools.delete_uploadfiles')
@log_decor
def delete_files(request):
    if request.method == 'GET':
        dele_id = request.GET["del_id"]
        exit_file_path = UploadFiles.objects.filter(id=dele_id).values("file_save_path")
        if exit_file_path and os.path.exists(exit_file_path[0]["file_save_path"]):
            os.remove(exit_file_path[0]["file_save_path"])
            UploadFiles.objects.filter(id=dele_id).delete()
        return HttpResponseRedirect(reverse('opstools:upfile'))

@login_required
@log_decor
@permission_required('opstools.delete_uploadfiles')
def down_files(request):
    if request.method == 'GET':
        file_save_path = request.GET["file_path"]
        file_name_obj =  UploadFiles.objects.filter(file_save_path=file_save_path).values("file_name")
        file_name = file_name_obj[0]["file_name"]
        print("----down_files---=",file_save_path,"-----file_name----=",file_name)
        file = open(file_save_path,'rb')
        resp = FileResponse(file)
        resp['Content-Type']='application/octet-stream'
        resp['Content-Disposition']='attachment;filename="%s"'%file_name
        return resp

@login_required
@log_decor
@permission_required('opstools.delete_scriptgroup')
def del_group_info(request):
    if request.method == 'POST':
        req_handler = request.POST
        tags = json.loads(req_handler["tag"])
        ScriptGroup.objects.filter(group_uniqu_tag=tags).delete()
        ScriptGroupExecSeq.objects.filter(script_group_tag=tags).delete()
        return JsonResponse({"ret": "sucessful","data":"/opstools/script_group_list"}, status=200,)

@login_required
@log_decor
@permission_required('opstools.change_scriptgroup')
def edit_group_info(request):
    data = {}
    if request.method == 'POST':
        req_handler = request.POST
        tags = req_handler["tags"]
        script_order = req_handler["script_order"]
        GT = GetDayTime()
        NOW_TIME = GT.get_now_time("%Y-%m-%d %H:%M:%S")
        ScriptGroupExecSeq.objects.filter(script_group_tag=int(tags)).update(\
            script_exce_order = script_order, create_time=NOW_TIME)
        ScriptGroup.objects.filter(group_uniqu_tag=int(tags)).update(update_time=NOW_TIME)
        data["exit_priv"] = user_privilges_info(request)
        return HttpResponseRedirect(reverse('opstools:scriptgroup'))
    else:
        req_handler = request.GET
        tags = req_handler["tag"]
        data["function_name"] = ScriptGroup.objects.filter(group_uniqu_tag=int(tags)).values(\
            "title_name")[0]["title_name"]
        exce_order = ScriptGroupExecSeq.objects.filter(script_group_tag=int(tags)).values(\
            "script_exce_order")[0]["script_exce_order"]
        data["data"] = json.loads(exce_order)
        data["tags"] = tags
        data["exit_priv"] = user_privilges_info(request)
        return  render(request, "opstools/edit_group_script.html", data)

@login_required
@log_decor
@permission_required('opstools.add_scriptgrouprelease')
def get_hosts_exec_script(request):
    data = {}
    if request.method == 'POST':
        req_handler = request.POST
        hosts_info = req_handler["ips"]
        hosts_name = hosts_info.split(":")[0]
        hosts_ip  = hosts_info.split(":")[1]
        file_title_name = req_handler["script_name"]
        src_path_info = ScriptGroup.objects.filter(title_name=file_title_name\
                        ).values("group_uniqu_tag", "relate_id__file_name", \
                        "relate_id__file_save_path")
        src_path_list = []
        src_file_list = []
        group_tags = src_path_info[0]["group_uniqu_tag"]

        for mid_var in src_path_info:
            src_path_list.append(mid_var["relate_id__file_save_path"])
            src_file_list.append(mid_var["relate_id__file_name"])
        script_exce_squ = ScriptGroupExecSeq.objects.filter(script_group_tag=group_tags).values("script_exce_order")
        script_exce_squ_list = json.loads(script_exce_squ[0]["script_exce_order"])

        tags = str(time.time()).replace(".", "")
        log_file_path = os.path.join(ANSY_RET_DIR, tags + ".log")
        auto_create_script = tags + ".sh"
        save_file_abs_path = os.path.join(UPFILE_PATH, auto_create_script)
        host_user = HostsInfo.objects.filter(name=hosts_name).values("ansible_user")
        DEST_FILE_PATH = "/home/%s/upfile/opsserver/exce-tags" % str(host_user[0]["ansible_user"])
        ret_status = auto_create_exce_group_script(script_exce_squ_list, save_file_abs_path, tags, log_file_path, DEST_FILE_PATH)
        mid_group_obj_list =  ScriptGroup.objects.filter(title_name=file_title_name)
        script_droup_obj = mid_group_obj_list[0]
        if not ret_status:
            ScriptGroupRelease.objects.create(group_uniqu_tag=tags, hosts_ip=hosts_ip, \
                            hosts_name=hosts_name, operator_user=request.user, log_path=log_file_path, 
                            release_script_name=auto_create_script, release_script_path=save_file_abs_path, \
                            relate_script_group=script_droup_obj, release_status=3)
            return HttpResponseRedirect(reverse('log:excescriptgroup'))
        ScriptGroupRelease.objects.create(group_uniqu_tag=tags, hosts_ip=hosts_ip, \
                                  hosts_name=hosts_name, operator_user=request.user, log_path=log_file_path, \
                                  release_script_name=auto_create_script, release_script_path=save_file_abs_path, \
                                  relate_script_group = script_droup_obj)
        src_path_list.append(save_file_abs_path)
        script_exce_squ_list.append(auto_create_script)
        async_exec_script_group.delay(log_file_path, hosts_name, tags, src_path_list, \
                                      script_exce_squ_list, DEST_FILE_PATH, auto_create_script)
        return HttpResponseRedirect(reverse('log:excescriptgroup'))
    else:
        obj = ScriptGroup.objects.values("title_name").distinct()
        data["obj"] = obj
        ips = HostsInfo.objects.values("id", "ip", "name")
        data["ips"] = ips
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opstools/get_hosts_exce_script.html", data)

@login_required
@log_decor
@permission_required('opstools.add_scriptgroup')
def create_group_script(request):
    data = {}
    if request.method == 'POST':
        req_handler = request.POST
        color_list = ["btn red", "btn yellow", "btn green", \
                    "btn  purple", "btn gray", "btn dark red", "btn black"]
        select_color = random.sample(color_list, 1)
        group_tags = int(str(time.time()).replace(".",""))
        name = req_handler["function_name"]
        script_name = req_handler.getlist("script_name")
        if ScriptGroup.objects.filter(title_name=name):
            data["error"] = "%s功能名存在，请重新定义名称。"%name
            return render(request, "opstools/create_group_script.html", data)
        ScriptGroupExecSeq.objects.create(script_exce_order = json.dumps(script_name), \
                                          script_group_tag = group_tags)
        for sc_name in script_name:
            upload_file_obj = UploadFiles.objects.get(file_name=sc_name)
            ScriptGroup.objects.create(group_uniqu_tag=group_tags, title_name=name, \
                    create_user=request.user, color_tags=select_color[0], relate_id=upload_file_obj)
        return HttpResponseRedirect(reverse('opstools:scriptgroup'))
    else:
        file_name_obj = UploadFiles.objects.filter(Q(file_name__endswith=\
                        ".py")|Q(file_name__endswith=".sh")).values("file_name")
        data["data"] = file_name_obj
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opstools/create_group_script.html", data)

@log_decor
def async_exce_script_ret(request):
    if request.method == 'POST':
        req_handle = request.POST
        tags = req_handle.get("group_tag", "")
        ret =  req_handle.get("ret", "2")
        print("-------async_exce_script_ret-st-----------", tags, "----------ret---------", ret)
        GT = GetDayTime()
        NOW_TIME = GT.get_now_time("%Y-%m-%d %H:%M:%S")
        print("-------async_exce_script_ret-mid-----------", ScriptGroupRelease.objects.filter(group_uniqu_tag=tags).values("release_status"))
        if ScriptGroupRelease.objects.filter(group_uniqu_tag=tags).values("release_status"):
            print("-------async_exce_script_ret--8888888888888-ed-----------")
            ScriptGroupRelease.objects.filter(group_uniqu_tag=tags).update(release_status=int(ret), update_time=NOW_TIME)
            print("-------async_exce_script_ret-ed-----------")
            return JsonResponse({"ret": "sucessful"}, status=200)
        return JsonResponse({"ret": "false"}, status=401)


@login_required
def get_script_list_api(request):
    if request.method == 'POST':
        req_handle = request.POST
        name = json.loads(req_handle.get("group_name", ""))
        group_id = ScriptGroup.objects.filter(title_name=name).values("group_uniqu_tag")[0]["group_uniqu_tag"]
        script_seq = ScriptGroupExecSeq.objects.filter(script_group_tag=group_id).values("script_exce_order")
        script_list = json.loads(script_seq[0]["script_exce_order"])
        mid_list = []
        for pos in range(len(script_list)):
            mid_list.append(str(pos+1)+")."+script_list[pos])
        script_list_str = ','.join(mid_list).replace(",","\n")
        return JsonResponse({"ret": "sucessful", "data":script_list_str}, status=200)
