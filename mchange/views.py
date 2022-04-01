import time
import json
from user.views import user_privilges_info
from release.models import HostsInfo, TaskInfo
from mirrors.mirror_api import GetDayTime
from opslog.log_api import  request_client_ip
from release.release_api import async_list_bash, async_sealing_version
from api.models import AsyncOperationAudit
from api.views import dingtalk_machine_api, log_decor

from .models import ChangeRecorder, HostsInfo, ServerMirror, ApplicationRecorder
from django.shortcuts import render, HttpResponseRedirect, reverse
from django.contrib.auth.decorators import login_required, permission_required
from .api import get_server_mirror

GT = GetDayTime()
SIXTY_DAY_AGO = GT.get_pre_later_time(-60, "%Y-%m-%d %H:%M:%S")
NOW_DAY = GT.get_pre_later_time(1, "%Y-%m-%d %H:%M:%S")

@login_required
@permission_required('mchange.scanf_changerecorder')
@log_decor
def change_recoder(request):
    data = {}
    if request.method == 'GET':
        ret = ChangeRecorder.objects.values("id", "before_warehouse_tags", "proposer", \
                           "after_warehouse_tags", "reason", "change_status", "change_time", \
                           "hostsinfo__name", "hostsinfo__ip").filter(\
                           change_time__range=[SIXTY_DAY_AGO, NOW_DAY]).order_by("-change_time")
        data["data"] = ret
    data["exit_priv"] = user_privilges_info(request)
    return render(request, 'mchange/mchange_list.html', data)

@login_required
@permission_required('mchange.add_changerecorder')
@log_decor
def add_change(request):
    data = {}
    if request.method == 'POST':
        st = time.time()
        req_handle = request.POST
        name = req_handle["name"]
#        ip = req_handle["ip"]
        warehouse_tags_list = req_handle.getlist("warehouse_tags")
        version = req_handle["version"]
        reason = req_handle["reason"]
        unique_id = str(time.time()).replace(".", "")
        request_ip = request_client_ip(request)
#        docker_handle = DockerRemoteApi()
        for i in warehouse_tags_list:
            mid_obj = ServerMirror.objects.filter(tag=i).values("repository", "hostsinfo_id__ip")
            src_image = mid_obj[0]["repository"]+i
#            mid_version = i[:i.rfind(":")+1]+version
            dest_image = "reg.xxxxxx.net/prod/"+i[:i.rfind(":")]
            remote_ip = mid_obj[0]["hostsinfo_id__ip"]
            dest_image_version = dest_image+":"+version
#            docker_handle.by_image_to_tag_push(remote_ip, src_image, dest_image, version)
            data = {"unique_tags":unique_id, "after_warehouse_tags":dest_image_version, \
                  "before_warehouse_tags":src_image, "proposer":name, "change_status":2, \
                  "reason":reason, "hostsinfo":HostsInfo.objects.get(ip=remote_ip)}
            ChangeRecorder.objects.create(**data)
            #change_obj = ChangeRecorder.objects.filter(unique_tags=unique_id, after_warehouse_tags=dest_image_version)
            #print("--------------change_obj-------------", change_obj)
            async_sealing_version.delay(remote_ip, src_image, dest_image, version, unique_id, dest_image_version)
            md = time.time()
            print("--st-md----=", md-st)
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        str_warehouse_tags = ';'.join(warehouse_tags_list)
        print("-----str_warehouse_tags----", str_warehouse_tags)
        send_info = "[提交封版申请]\n申请人  ：%s\n申请时间 ：%s\n封版前容器: %s\n预制版本 ：%s\n申请原因 ：%s\
                     "%(name, str(now_time), str_warehouse_tags, version, reason)
        print("-----send_info------", send_info)
        dingtalk_machine_api(send_info)
        return HttpResponseRedirect('/mchange/change_recoder/')
    else:
        req_handle = request.GET
        judge_release = req_handle.getlist("batch_release")
        if judge_release:
            data["ensure_result"] = True
        # mirrors = MirrorTags.objects.values("name","warehouser__name")
        test_env_ip_list = ["172.29.86.143", "172.29.86.80"]
        #get_server_mirror("testapp")
        get_server_mirror(test_env_ip_list)
        #ips = HostsInfo.objects.filter(name="testapp").values("ip", "name")
        mirrors = ServerMirror.objects.values("repository", "tag")
        data["mirros"] = mirrors
        data["ips"] = test_env_ip_list
        data["exit_priv"] = user_privilges_info(request)
        #print("ips----", ips)
        return render(request, 'mchange/add_change.html', data)

@login_required
@log_decor
def sealing_release(request):
    data = {}
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    if request.method == "POST":
        req_handle = request.POST
        user = request.user
        ips_list = req_handle.getlist("ips")
        id_str = req_handle["id_list"]
        if  '[' in id_str:
            id_list = json.loads(id_str)
        else:
            id_list = id_str.split(',')

        tname = str(time.time()).replace(".", "")
        hosts_name_list = []
        str_param_list = []
        for  id  in id_list:
            crecorder_src_data = ChangeRecorder.objects.filter(id=id).values(\
                   "after_warehouse_tags", "hostsinfo__name")
            str_warehouse_tags = crecorder_src_data[0]["after_warehouse_tags"]
    #        hosts_name = crecorder_src_data[0]["hostsinfo__name"]
            for  i in ips_list:
                hosts_name = i[:i.find(":")]
                middle_str_param = " ansible %s -m raw -a \"sh service-create-or-update.sh %s\"" \
                    % (hosts_name, str_warehouse_tags)
                hosts_name_list.append(hosts_name)
                str_param_list.append(middle_str_param)
                TaskInfo.objects.create(name=tname, warehouse_tags=str_warehouse_tags, \
                                        need_exce_param=middle_str_param, \
                                        exscript="service-create-or-update.sh", \
                                        releaser=user, release_status=2, task_source=2, \
                                        hostsinfo=HostsInfo.objects.get(name=hosts_name))
            hosts = ','.join(list(set(hosts_name_list)))
            data["hosts"] = hosts
            exscript = "service-update.sh"
            data["exscript"] = exscript
            data["need_exce_param"] = str_param_list
            data["id"] = ','.join(id_list)
            data["name"] = tname
            data["exit_priv"] = user_privilges_info(request)
        return render(request, "release/constrast_check_network.html", data)
    else:
        req_handle = request.GET
        id_list = req_handle["exce_id"]
        if  '[' in id_list:
            id_list = json.loads(id_list)
        else:
            id_list = id_list.split(',')

        tags_list = []
        for  i  in id_list:
            tags = ChangeRecorder.objects.filter(id=i).values("after_warehouse_tags")
            if AsyncOperationAudit.objects.filter(unique_code=i).filter(release_status=0).exists():
                tags_list.append(tags[0])
            else:
                data["error"] = "The %s imgae is not exit"%tags[0]["after_warehouse_tags"]
                break
        ips = HostsInfo.objects.values("ip", "name")
        data["ips"] = ips
        data["user"] = request.user
        data["ip"] = ip
        data["tags_list"] = tags_list
        data["id_list"] = json.dumps(id_list)
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'mchange/release_mchange.html', data)

@log_decor
def apply_change_list(request):
    data = {}
    if request.method == "GET":
        ret = ApplicationRecorder.objects.values("id", "apply_user", "project_name", \
              "project_branch", "bug_id", "reasons", "change_type", "apply_status").order_by("-id")
        data["data"] = ret
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'mchange/apply_change_list.html', data)

@log_decor
def apply_change(request):
    data = {}
    if request.method == "POST":
        req_handle = request.POST
        proposer = req_handle["proposer"]
        project = req_handle["project"]
        bug_id = req_handle["bug_id"]
        issue_version = req_handle["issue_version"]
        change_type = req_handle["change_type"]
        change_reason = req_handle["change_reason"]
        ApplicationRecorder.objects.create(apply_user=proposer, project_name=project, \
                                           project_branch=issue_version, bug_id=bug_id, \
                                           reasons=change_reason, change_type=change_type)

        send_info = "[提交变更申请]\n申请人 ：%s\n工程 ： %s\n 禅道BUG ID ：%s\n问题版本 ：%s\n变更类型 ：%s\n 变更原因 : %s"\
                    %(proposer, project, bug_id, issue_version, change_type, change_reason)
        dingtalk_machine_api(send_info)
        data["exit_priv"] = user_privilges_info(request)
        return HttpResponseRedirect('/mchange/apply_change_list/')
    else:
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'mchange/apply_add_record.html', data)
