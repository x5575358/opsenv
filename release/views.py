from __future__ import unicode_literals
import os, time
import json
from user.views import user_privilges_info
from django.shortcuts import render, reverse
from django.http import JsonResponse
from django.http import  HttpResponse, HttpResponseRedirect

from api.get_run_container import get_container_list, list_trans_dict, compare_dict
from api.open_api import bash, read_file
from api.views import log_decor
from Ops.settings import  ANSY_RET_DIR, UAT_HOSTS, TEST_HOSTS
from opslog.log_api import  logger, create_execLog, request_client_ip
from mirrors.models import MirrorTags
from .release_api import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from asset.models import Ec2AssetInfo
from opscontainer.models import ContainerEnvGroup, ContainerEnv

from .models import *
from opstools.models import UploadFiles

@login_required
@permission_required('release.scanf_taskinfo', login_url=login_url)
@log_decor
def task_list(request):
    data = {}
    obj = TaskInfo.objects.filter(release_status=1).values("id", "name", "release_status", \
                  "exscript", "creation_time", "warehouse_tags", \
                  "update_time", "hostsinfo__name", "hostsinfo__ip").order_by('-id')
    data["exit_priv"] = user_privilges_info(request)
    data['data'] = code_trans_lang(obj)
    return render(request, 'release/task_list.html', data)

@login_required
@permission_required('release.scanf_asyncrecord')
@log_decor
def history_task_list(request):
    data = {}
    obj = TaskInfo.objects.exclude(release_status=1).values("id", "name", "release_status", \
                  "exscript", "creation_time", "warehouse_tags", "update_time", \
                  "hostsinfo__name", "hostsinfo__ip").order_by('-creation_time')
    data["exit_priv"] = user_privilges_info(request)
    data['data'] = code_trans_lang(obj)
    return render(request, 'release/history_task_list.html', data)


@login_required
@permission_required('release.scanf_hostinfo')
@log_decor
def hosts_list(request):
    data = {}
    ret = HostsInfo.objects.values("id", "name", "ip", "ansible_user", "creation_time", "available_condition")
    data['data'] = code_trans_lang(ret)
    data["exit_priv"] = user_privilges_info(request)
    return render(request, 'release/hosts_list.html', data)

@login_required
@permission_required('release.add_hostsinfo')
@log_decor
def add_hosts(request):
    data = {}
    if request.method == 'POST':
        req_handle = request.POST
        name = req_handle["name"]
        ip = req_handle["ip"]
        private_key = req_handle["private_key"]
        ansible_user = req_handle["ansible_user"]
        if HostsInfo.objects.filter(name=name):
            return render(request, 'release/add_hosts.html', {"error":"该主机名已经\
                  存在，请不要重复添加！"})
        else:
            host_object = HostsInfo.objects.values("id").order_by('-creation_time')
            need_order = "%s ansible_ssh_private_key_file=%s ansible_user=%s"%(ip, private_key, ansible_user)
            need_add_data = {"[%s]"%name: need_order}
            logger.debug("-------need_add_data-----------%s"%need_add_data)
            HostsInfo.objects.create(name=name, ip=ip, private_key=private_key, \
                     ansible_user=ansible_user)
            logger.debug("-------host_object-----------%s"%host_object)
            if len(host_object) > 1:
                host_id = host_object[1]["id"]
                logger.debug("--------update_ansible_host_file--st-%s"%host_id)
                update_ansible_host_file(host_id, need_add_data, HostsInfo.objects.get(name = name), request.user)
            else:
                host_id = ""
                logger.debug("--------update_ansible_host_file--st-")
                update_ansible_host_file(host_id, need_add_data, HostsInfo.objects.get(name = name), request.user)
            logger.debug("--------update_ansible_host_file--end-")
        return HttpResponseRedirect('/release/hosts_list/')
    else:
        cmd = "ls /home/centos/pem/*.pem"
        ret_value = bash(cmd)
        mid_ret_value_list = ret_value.split("\n")[:-1]
        ret_value_list = [value.split("/")[-1] for value in mid_ret_value_list]
        data["pems"] = ret_value_list
        data["ips"] = Ec2AssetInfo.objects.values("private_ip")
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'release/add_hosts.html', data)

@login_required
def del_hosts(request):
    data = {}
    if request.method == 'GET':
        req_handle = request.GET
        del_id = req_handle.get("del_id", "")
        print("------del_id-----------", del_id)
        obj = AnsibleHostFile.objects.filter(relate_hostifo_key__id=del_id).values("json_file_path", "json_file_name")
        print("------obj-----------", obj)
        json_file = os.path.join(obj[0]["json_file_path"], obj[0]["json_file_name"])
        print("------json_file-----------", json_file)
        os.remove(json_file)
        AnsibleHostFile.objects.filter(relate_hostifo_key__id=del_id).delete()
        print("------host_name_obj---st--------")
        host_name_obj = HostsInfo.objects.filter(id=del_id).values("name")
        print("------host_name_obj---ed--------", host_name_obj)
        host_name = host_name_obj[0]["name"]
        print("------host_name--------", host_name)
        read_cmp_delete_data(host_name)
        print("------read_cmp_delete_data-----ed---")
        HostsInfo.objects.filter(id=del_id).delete()
        return HttpResponseRedirect(reverse('in_release:hostslist'))


@login_required
@permission_required('release.add_taskinfo')
@log_decor
def add_task(request):
    data = {}
    if request.method == 'POST':
        req_handle = request.POST
        name = req_handle["name"]
        tags_ip = req_handle["ip"]
        if ":" not in tags_ip:
            mirrors = MirrorTags.objects.values("name", "warehouser__name")
            ips = HostsInfo.objects.values("ip", "name")
            data["mirros"] = mirrors
            data["ips"] = ips
            data["error"] = "目的IP-标签为空，请重新添加！"
            return render(request, 'release/add_task.html', data)
        ret_ip = tags_ip.split(":")[1]
        hostsname = tags_ip.split(":")[0]
        optname = req_handle["optname"]
        exscript = req_handle["exscript"]
        warehouse_tags = req_handle.getlist("warehouse_tags")

        exce_code = AnsibleExceMode.objects.filter(name=optname).values("code")
        param_list = []
        warehouse_tags_list = []
        user = request.user
        for tags in warehouse_tags:
            str_warehouse_tags = str(tags)
            warehouse_tags_list.append(str_warehouse_tags)
            if "cat" == optname:
                exce_param = exce_code[0]["code"]%(hostsname, exscript)
            elif "sh" == optname:
                end_param = "reg.xxxxxx.net/"+str_warehouse_tags
                exce_param = exce_code[0]["code"] %(hostsname, exscript, end_param)
                TaskInfo.objects.create(name=name, warehouse_tags=str_warehouse_tags, \
                     need_exce_param=exce_param, exscript=exscript, releaser=user, \
                     release_status=1, hostsinfo=HostsInfo.objects.get(ip=ret_ip))
        return HttpResponseRedirect('/release/task_list/')

    else:
        mirrors = MirrorTags.objects.values("name", "warehouser__name")
        ips = HostsInfo.objects.values("ip", "name")
        data["mirros"] = mirrors
        data["ips"] = ips
        data["opt"] = ['cat', 'sh']
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'release/add_task.html', data)

@login_required
@permission_required('release.delete_taskinfo')
def del_task(request):
    if request.method == "GET":
        rep_handle = request.GET
        id = rep_handle["del_id"]
        try:
            TaskInfo.objects.filter(id=id).delete()
        except Exception as err:
            print(err)
    return HttpResponseRedirect('/release/task_list/')

@login_required
@permission_required('release.change_taskinfo')
def edit_task(request):
    return HttpResponseRedirect('/release/task_list/')
    if request.method == "POST":
        rep_handle = request.POST
        id = rep_handle["edit_id"]
    else:
        return HttpResponseRedirect('/release/task_list/')

@login_required
@permission_required('release.add_taskinfo')
def exec_task(request):
    data = {}
    if request.method == "GET":
        rep_handle = request.GET
        id = rep_handle["exec_id"]
        hosts_auth_name = TaskInfo.objects.filter(id=id).values("hostsinfo__name", \
                          "hostsinfo__ip", "exscript", "need_exce_param")
        host = hosts_auth_name[0]["hostsinfo__name"]
        data["hosts"] = host
        exscript = hosts_auth_name[0]["exscript"]
        data["exscript"] = exscript
        ip = hosts_auth_name[0]["hostsinfo__ip"]
        data["ip"] = ip
        need_exce_param = hosts_auth_name[0]["need_exce_param"].split(",")
        data["need_exce_param"] = need_exce_param
        data["exit_priv"] = user_privilges_info(request)
        data["id"] = id
    return render(request, "release/check_network.html", data)

@login_required
@permission_required('release.add_taskinfo')
@log_decor
def load_exce_data(request):
    data = {}
    if not os.path.exists(ANSY_RET_DIR):
        os.mkdir(ANSY_RET_DIR)
    if request.method == "GET":
        rep_handle = request.GET
        id_isornot_list = rep_handle["exce_id"].replace("\'", "")
        for id in  id_isornot_list.split(','):
            affinfo = AffirmInfo.objects.filter(ftaskinfo=id).values("pk", "hosts_tags", \
                      "order_param")
            taskinfo = TaskInfo.objects.filter(id=id).values("hostsinfo__ip", "task_source", \
                      "warehouse_tags", "hostsinfo__name", "history_version", "history_warehouse")
            dest_name = taskinfo[0]["hostsinfo__name"]
            version = taskinfo[0]["history_version"]
            warehouse = taskinfo[0]["history_warehouse"]
            ContrastResult.objects.filter(dest_warehouse_name=warehouse, dest_version=version, \
                            dest_host_name=dest_name).filter(Q(current_status=0)|Q(current_status=1)).update(current_status=3)
            tags = taskinfo[0]["warehouse_tags"]
            #ContrastOfResult.objects.filter(test_name=tags).update(status=1)
            soucrce_code = taskinfo[0]["task_source"]
            for single_affinfo in affinfo:
                needexce = single_affinfo["order_param"]
                pk = single_affinfo["pk"]
                taskinfo = TaskInfo.objects.filter(id=id).values("hostsinfo__ip")
                ip = taskinfo[0]["hostsinfo__ip"]
                str_needexce = needexce.replace("[", "").replace("]", "").replace("'", "")
                needexce_list = str_needexce.split(",")
                for exec_param in needexce_list:
                    file_name = str(pk) + "_" + str(time.time()) + ".txt"
                    file_path = os.path.join(ANSY_RET_DIR, file_name)
                    mid_var = exec_param.split("\"")
                    warehouse_tags = mid_var[1]
                    exec_head = mid_var[0]
                    release_async_bash_exec.delay(exec_param, file_path, ip, pk, id, \
                                            warehouse_tags, exec_head)
                    AffirmInfo.objects.filter(ftaskinfo=id).update(release_status=3)
                    TaskInfo.objects.filter(id=id).update(release_status=3)
                    AsyncRecord.objects.create(file_name=file_name, file_path=file_path, \
                                release_status=2, affirm_id=AffirmInfo.objects.get(pk=pk))
                    logger.info("exce releasing !")
        if soucrce_code == 1:
            return HttpResponseRedirect('/release/get_difference_container/')

    return HttpResponseRedirect('/release/task_list/')

def open_api(request):
    if request.method == "GET":
        JsonResponse({"ret":"执行中"})
        return HttpResponse("sss")

@login_required
def check_network(request):
    data = {}
    if request.method == "GET":
        rep_handle = request.GET
        id = rep_handle["exce_id"]
        user = request.user
        hosts_auth_name = TaskInfo.objects.filter(id=id).values("hostsinfo__name", \
                          "warehouse_tags", "hostsinfo__ip", "exscript", "need_exce_param", \
                          "task_source")
        host = hosts_auth_name[0]["hostsinfo__name"]
        data["hosts"] = host
        exscript = hosts_auth_name[0]["exscript"]
        data["exscript"] = exscript
        ip = hosts_auth_name[0]["hostsinfo__ip"]
        data["ip"] = ip

        ping_order = "ansible %s -m ping" % host
        file_order = "ansible %s -m command -a \"ls %s \"" % (host, exscript)
        ping_ret = bash(ping_order)
        data["dest_net_status"] = ret_judge(ping_ret)
        data["task_source"] = hosts_auth_name[0]["task_source"]

        if ret_judge(ping_ret) == "0":
            needexce = hosts_auth_name[0]["warehouse_tags"]
            str_needexce = needexce.replace("[", "").replace("]", "").replace("'", "")
            needexce_list = str_needexce.split(";")
            for images in needexce_list:
                exec_order = "docker pull %s 1>/dev/null 2>/dev/null " % images
                release_async_bash.delay(exec_order)
                warehouse = images[:images.find(":") + 1]
                last_version_order = "ansible %s -m command -a \"docker ps\"|grep %s|\
                                     awk -F \" \" \'{print $2}\'"% (host, warehouse)
                last_version_ret = bash(last_version_order)
                LastVersionRecord.objects.create(version_id=last_version_ret, \
                                  need_update_version=images, user=user, \
                                  ftaskinfo=TaskInfo.objects.get(id=id))
            file_ret = bash(file_order)
            data["dest_file_status"] = ret_judge(file_ret)
            result_list = []
            result_list.append(ping_ret)
            result_list.append(file_ret)
            data["result_info"] = result_list
            need_exce_param = hosts_auth_name[0]["need_exce_param"].split(",")
            data["need_exce_param"] = need_exce_param
            data["id"] = id
            data["exit_priv"] = user_privilges_info(request)
            if data["dest_net_status"] == "0" and data["dest_file_status"] == "0":
                for param in need_exce_param:
                    AffirmInfo.objects.create(ip=ip, hosts_tags=host, order_param=param, \
                               releaser=user, release_status=2, \
                               ftaskinfo=TaskInfo.objects.get(id=id))
    return render(request, "release/exce_task.html", data)

def ret_judge(retinfo):
    if "SUCCESS" in retinfo:
        return "0"
    elif "FAILED" in retinfo:
        return "1"
    else:
        return "3"

@login_required

def scanf_exce_detail(request):
    data = {}
    if request.method == "GET":
        rep_handle = request.GET
        id = rep_handle["detail_id"]
        hosts_auth_name = TaskInfo.objects.filter(id=id).values("hostsinfo__name", \
                          "hostsinfo__ip", "exscript", "need_exce_param", "release_status")
        host = hosts_auth_name[0]["hostsinfo__name"]
        data["hosts"] = host
        exscript = hosts_auth_name[0]["exscript"]
        data["exscript"] = exscript
        ip = hosts_auth_name[0]["hostsinfo__ip"]
        data["ip"] = ip
        need_exce_param = hosts_auth_name[0]["need_exce_param"].split(",")
        data["need_exce_param"] = need_exce_param
        data["id"] = id
        task_status = hosts_auth_name[0]["release_status"]
        affirm_status = task_trans_status(task_status)
        affirm_info = AffirmInfo.objects.filter(ftaskinfo=id).filter(release_status=affirm_status\
                      ).values("id")
        ret_detail = []
        for single_affirm_info in affirm_info:
            affirm_id = single_affirm_info["id"]
            file_path_list = AsyncRecord.objects.filter(affirm_id_id=affirm_id).values("file_path")
            for p in file_path_list:
                f_content = read_file(p["file_path"])
                print("-----f_content-----",f_content)
                ret_detail.append(f_content.replace("\n","<br>"))
        data["exit_priv"] = user_privilges_info(request)
        data["dest_net_status"] = "0"
        data["dest_file_status"] = "0"
        data["result_info"] = ret_detail
        return render(request, "release/scanf_exce_detail.html", data)
        # return HttpResponse("scanf_exe3c_detail")

def task_trans_status(code):
    if code == 0:
        return 0
    elif code == 1:
        return 2
    elif code == 3:
        return 3
    elif code == 4:
        return 1
    elif code == 5:
        return 4

def code_trans_lang(listinnerdict):
    i = 1
    for o in listinnerdict:
        o.update({'only_sign':'%5d'%i})
        #if o["release_status"] == 0:
         #   o["release_status"] = "执行成功"
#        elif o["release_status"] == 1:
 #           o["release_status"] = "未发布"
  #      elif o["release_status"] == 2:
   #         o["release_status"] = "发布未执行"
    #    elif o["release_status"] == 3:
     #       o["release_status"] = "执行中"
#        elif o["release_status"] == 4:
 #           o["release_status"] = "执行失败"
  #      elif o["release_status"] == 5:
   #         o["release_status"] = "执行超时"
        i = i+1
    return listinnerdict


@login_required
@permission_required('release.scanf_contrastresult')
@log_decor
def get_difference_container(request):
    data = {}
    if request.method == "GET":
        single_exit_container = ContrastResult.objects.filter(current_status=1).values("id", "src_host_name", \
                    "src_warehouse_name", "src_version", "dest_env_group_name")
        diff_data =  ContrastResult.objects.filter(current_status=0).values("id", "src_host_name", \
                    "src_warehouse_name", "src_version", "dest_host_name", "dest_warehouse_name", \
                    "dest_version")
        selected_data = ContrastResult.objects.filter(Q(current_status=0)|Q(current_status=1)).values("src_env_group_name", "dest_env_group_name")
        src_selected = ""
        dest_selected = ""
        if selected_data:
            src_selected = selected_data[0]["src_env_group_name"]
            dest_selected = selected_data[0]["dest_env_group_name"]
        container_group_obj = ContainerEnvGroup.objects.filter(~Q(name=src_selected),~Q(name=dest_selected)).values("name").distinct()
        data["src_container_group"] = container_group_obj
        data["dest_container_group"] = container_group_obj
        data["src_selected"] = src_selected
        data["dest_selected"] = dest_selected
        data["single_exit_container"] = single_exit_container
        data["data"] = diff_data
        data["exit_priv"] = user_privilges_info(request)
        print("1111111111111111111111111111", user_privilges_info(request))
        return render(request, 'release/difference_container_list.html', data)
    else:
        req_handle = request.POST
        src_name = json.loads(req_handle["src_name"])
        dest_name = json.loads(req_handle["dest_name"])
        print("---src_name---", src_name, "-----dest_name----", dest_name)
        #ContrastResult.objects.filter(~Q(current_status=3)).update(current_status=4)
        ContrastResult.objects.filter(~Q(current_status=3)).delete()
        src_group_name_obj = ContainerEnvGroup.objects.filter(name=src_name).values("relation_env__name").distinct()
        dest_group_name_obj = ContainerEnvGroup.objects.filter(name=dest_name).values("relation_env__name").distinct()
        src_group_obj = ContainerEnvGroup.objects.filter(name=src_name).values("relation_env__relation_hostinfo__ip", \
                        "relation_env__relation_hostinfo__name", "relation_env__name")
        dest_group_obj = ContainerEnvGroup.objects.filter(name=dest_name).values("relation_env__relation_hostinfo__ip", \
                        "relation_env__relation_hostinfo__name", "relation_env__name")
        src_data_list = env_group_get_container(src_name, src_group_name_obj, src_group_obj) 
        dest_data_list = env_group_get_container(dest_name, dest_group_name_obj, dest_group_obj)
        tag = str(time.time()).replace(".", "")
        constrat_container_group(src_data_list, dest_data_list, tag)
        return JsonResponse({"data": ""}, status=200)

@login_required
@permission_required('release.change_contrastofresult')
@log_decor
def update_difference_container(request):
    data = {}
    print("-----------------jr----################",request.session)
    if request.method == "GET":
        single_exit_ret_dict = {}
        print("-----------------i12344jr----################")
        ContrastOfResult.objects.all().delete()
        print("------type---TEST_HOSTS--------",TEST_HOSTS)
        print("------type---TEST_HOSTS--------",type(TEST_HOSTS))
        for h_test in TEST_HOSTS:
            test_env, test_dict = get_container_list(h_test)
            print("---------h_test-------",h_test)
            for h_uat in UAT_HOSTS:
                print("------------h_uat--------",h_uat)
                uat_env, uat_dict = get_container_list(h_uat)
                uat_container_dict = list_trans_dict(uat_dict)
                test_container_dict = list_trans_dict(test_dict)
                single_exit_dict, diff_version_list = compare_dict(test_container_dict,uat_container_dict)
                single_exit_ret_dict.update(single_exit_dict)
                for diff_ver in diff_version_list:
                    ContrastOfResult.objects.create(test_name=list(diff_ver[1].keys())[0], \
                                     test_container_hosts=list(diff_ver[1].values())[0], \
                                     uat_name=list(diff_ver[0].keys())[0], status=0, \
                                     uat_container_hosts=list(diff_ver[0].values())[0])
        for keys, values in single_exit_ret_dict.items():
            ContrastOfResult.objects.create(test_name=keys, test_container_hosts=values, \
                             uat_name="", uat_container_hosts="", status=0)
        return HttpResponseRedirect('/release/get_difference_container/')

@login_required
#@permission_required('release.change_taskinfo')
@log_decor
def exec_synchronization_container(request):
    data = {}
    if request.method == "POST":
        rep_handle = request.POST
        id_str = rep_handle["exce_id"]
        hosts_name_list = []
        str_param_list = []
        user = request.user
        tname = str(time.time()).replace(".", "")
        if  '[' in id_str:
            id_list = json.loads(id_str)
        else:
            id_list = id_str.split(',')
        for ids in id_list:
            mid_obj = ContrastResult.objects.filter(id=int(ids)).values("src_warehouse_name", \
                      "src_version", "dest_host_name", "dest_warehouse_name", "dest_version")
            dest_hosts_name = mid_obj[0]["dest_host_name"]
            dest_version = mid_obj[0]["dest_version"]
            dest_warehouse = mid_obj[0]["dest_warehouse_name"]
            str_warehouse_tags = mid_obj[0]["src_warehouse_name"]+ mid_obj[0]["src_version"]
            middle_str_param = " ansible %s -m raw -a \"sh service-create-or-update.sh %s\"" % (dest_hosts_name, \
                               str_warehouse_tags)
            str_param_list.append(middle_str_param)
            hosts_name_list.append(dest_hosts_name)
            TaskInfo.objects.create(name=tname, warehouse_tags=str_warehouse_tags, \
                     need_exce_param=middle_str_param, exscript="service-create-or-update.sh", \
                     releaser=user, release_status=1, task_source=1, history_warehouse=dest_warehouse, \
                     history_version=dest_version, hostsinfo=HostsInfo.objects.get(name=dest_hosts_name))
        ret_data = "/release/exec_synchronization_container/?tag=%s"%tname
        return JsonResponse({"data": ret_data}, status=200)
    else:
        rep_handle = request.GET
        tag = rep_handle["tag"]
        obj = TaskInfo.objects.filter(name=tag).values("id", "need_exce_param", "exscript")
        data["hosts"] = TaskInfo.objects.filter(name=tag).values("hostsinfo__name","hostsinfo__ip").distinct()
        data["exscript"] = obj[0]["exscript"]
        data["need_exce_param"] = obj
        data["name"] = tag
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "release/constrast_check_network.html", data)

@login_required
@log_decor
def constrast_check_network(request):
    data = {}
    if request.method == "GET":
        st = time.time()
        rep_handle = request.GET
        name = json.loads(rep_handle["exce_name"])
        op_user = request.user
        obj = TaskInfo.objects.filter(name=name).values("id", "hostsinfo__name", "history_warehouse", \
              "history_version", "warehouse_tags", "hostsinfo__ip", "need_exce_param", "task_source")
        unqiue_taskinfo_obj = TaskInfo.objects.filter(name=name).values("hostsinfo__name", \
                              "hostsinfo__ip", "exscript").distinct()
        single_exscript = unqiue_taskinfo_obj[0]["exscript"]
        data["exscript"] = single_exscript
        data["exce_param"] = TaskInfo.objects.filter(name=name).values("need_exce_param")
        data["hosts"] = TaskInfo.objects.filter(name=name).values("hostsinfo__name").distinct()
        data["task_source"] = obj[0]["task_source"]
        data["exit_priv"] = user_privilges_info(request)
        data["name"] = name
        network_jduge_list = []
        id_list = []
        for mid_obj in unqiue_taskinfo_obj:
            dest_hosts_name = mid_obj["hostsinfo__name"]
            dest_ip =  mid_obj["hostsinfo__ip"]
            
            ping_order = "ansible %s -m ping" %dest_hosts_name
            file_order = "ansible %s -m command -a \"ls %s \"" %(dest_hosts_name, single_exscript)
            mid_file_ret = bash(file_order)
            mid_ping_ret = bash(ping_order)
            network_jduge_list.append(mid_file_ret)
            network_jduge_list.append(mid_ping_ret)
            if ret_judge(mid_ping_ret) != "0":
                data["result_info"] = network_jduge_list
                data["id"] = ','.join(id_list)
                return render(request, "release/exce_task.html", data) 
            elif ret_judge(mid_file_ret) != "0 ":
                host_pwd_name = HostsInfo.objects.filter(name=dest_hosts_name).values("ansible_user")[0]["ansible_user"]
                exit_script = UploadFiles.objects.filter(file_name=single_exscript).values("file_save_path")[0]["file_save_path"]
                copy_file_order = "ansible %s -m copy -a \"src=%s dest=/home/%s\""%(dest_hosts_name, exit_script, host_pwd_name)
                bash(copy_file_order)
        for mid in obj:
            mid_id = mid["id"]
            id_list.append(str(mid_id))
            mid_ip = mid["hostsinfo__ip"]
            mid_name = mid["hostsinfo__name"]
            need_exec_param = mid["need_exce_param"]
            warehouse_tag = mid["warehouse_tags"]
            history_warehouse = mid["history_warehouse"]+mid["history_version"]
            need_warehouse = mid["warehouse_tags"]
            exec_order = "docker pull %s 1>/dev/null 2>/dev/null "%warehouse_tag
            release_async_bash.delay(exec_order)
            LastVersionRecord.objects.create(version_id=history_warehouse, need_update_version=need_warehouse, \
                              user=op_user, ftaskinfo=TaskInfo.objects.get(id=mid_id))
            AffirmInfo.objects.create(ip=mid_ip, hosts_tags=mid_name, order_param=need_exec_param, \
                              releaser=op_user, release_status=2, ftaskinfo=TaskInfo.objects.get(id=mid_id))
        code = "0"
        data["dest_net_status"] = code
        data["dest_file_status"] = code
        data["result_info"] = network_jduge_list
        data["id"] = ','.join(id_list)
        ed = time.time()
        print("-----spend--time-------", str(ed-st))
        return render(request, "release/exce_task.html", data) 


@login_required
@log_decor
def cancel_check_network(request):
    if request.method == "GET":
        rep_handle = request.GET
        name = rep_handle["exce_name"]
        task_name = TaskInfo.objects.filter(name=name).exists()
        if task_name:
            task_source_list = TaskInfo.objects.filter(name=name).values("task_source")
            print("---task_source_list-------", task_source_list)
            task_source = task_source_list[0]["task_source"]
            print("---task_source-------", task_source)
            TaskInfo.objects.filter(name=name).delete()
            last_name = LastVersionRecord.objects.filter(ftaskinfo__name=name).exists()
            if last_name:
                LastVersionRecord.objects.filter(ftaskinfo__name=name).delete()
            affir_name = AffirmInfo.objects.filter(ftaskinfo__name=name).exists()
            if affir_name:
                AffirmInfo.objects.filter(ftaskinfo__name=name).delete()
            if task_source == 0:
                return HttpResponseRedirect(reverse('in_release:task_list'))
            elif task_source == 1:
                return HttpResponseRedirect(reverse('in_release:diff_container'))
            elif task_source == 2:
                return HttpResponseRedirect(reverse('mchange:mchange_list'))
        else:
            return HttpResponseRedirect(reverse('in_release:diff_container'))

@login_required
@permission_required('release.add_contrastresult')
def after_constrat_add_task(request):
    data = {}
    if request.method == 'POST':
        req_handle = request.POST
        warehouse_tag = req_handle["warehouse_tag"]
        host_info = req_handle["hostinfo"]
        id_code =req_handle["id_code"]
        dest_hosts_name = host_info.split(":")[0]
        print("-----dest_hosts_name------",dest_hosts_name)
        print("------id_code---", id_code)
        print("------warehouse_tag---", warehouse_tag)
        name = str(time.time()).replace(".", "")
        exce_param =  "ansible %s -m raw -a \"sh service-create-or-update.sh %s\""%(dest_hosts_name, warehouse_tag)
        TaskInfo.objects.create(name=name, warehouse_tags=warehouse_tag, \
                 need_exce_param=exce_param, exscript="service-create-or-update.sh", \
                 releaser=request.user, release_status=1, task_source=1, \
                 hostsinfo=HostsInfo.objects.get(name=dest_hosts_name))
        data["hosts"] = dest_hosts_name
        exscript = "service-create-or-update.sh"
        data["exscript"] = exscript
        data["ip"] = host_info.split(":")[1]
        data["need_exce_param"] = exce_param
        data["name"] = name
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "release/new_add_check_network.html", data)
    else:
        req_handle = request.GET
        exce_id = req_handle["exce_id"]
        mirrors = ContrastResult.objects.filter(id=exce_id).values("unique_id", "dest_env_group_name", \
                        "src_warehouse_name", "src_version")
        group_name =  mirrors[0]["dest_env_group_name"]
        env_obj = ContainerEnvGroup.objects.filter(name=group_name).values("relation_env__name").distinct()
        ip_list = []
        for mid_obj in env_obj:
            mid_name = mid_obj["relation_env__name"]
            mid_list = ContainerEnv.objects.filter(name=mid_name).values("relation_hostinfo__name", "relation_hostinfo__ip")
            ip_list = ip_list + list(mid_list)
        data["mirros"] = mirrors
        data["ips"] = ip_list
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'release/after_constrat_add_task.html', data)

@login_required
def constrast_new_add_check_network(request):
    data = {}
    if request.method == "GET":
        st = time.time()
        rep_handle = request.GET
        name = json.loads(rep_handle["exce_name"])
        op_user = request.user
        obj = TaskInfo.objects.filter(name=name).values("id", "hostsinfo__name", "history_warehouse", \
              "history_version", "warehouse_tags", "hostsinfo__ip", "need_exce_param", "task_source", \
			  "exscript")
        id_list = []
        id_list.append(str(obj[0]["id"]))
        dest_hosts_name = obj[0]["hostsinfo__name"]
        single_exscript = obj[0]["exscript"]
        need_exce_param = obj[0]["need_exce_param"]
        data["exscript"] = single_exscript
        data["exce_param"] = [{"need_exce_param":need_exce_param}]
        data["hosts"] = [{"hostsinfo__name":dest_hosts_name}]
        data["task_source"] = obj[0]["task_source"]
        data["name"] = name
        ping_order = "ansible %s -m ping" %dest_hosts_name
        mid_ping_ret = bash(ping_order)
        network_jduge_list = []
        network_jduge_list.append(mid_ping_ret)
        if ret_judge(mid_ping_ret) != "0":
            data["result_info"] = network_jduge_list
            data["id"] = ','.join(id_list)
            return render(request, "release/exce_task.html", data)

        host_pwd_name = HostsInfo.objects.filter(name=dest_hosts_name).values("ansible_user")[0]["ansible_user"]
        exit_script = UploadFiles.objects.filter(file_name=single_exscript).values("file_save_path")[0]["file_save_path"]
        copy_file_order = "ansible %s -m copy -a \"src=%s dest=/home/%s\""%(dest_hosts_name, exit_script, host_pwd_name)
        bash(copy_file_order)
        need_warehouse = obj[0]["warehouse_tags"]
        exec_order = "docker pull %s 1>/dev/null 2>/dev/null "%need_warehouse
        release_async_bash.delay(exec_order)
        LastVersionRecord.objects.create(version_id=obj[0]["history_warehouse"], need_update_version=need_warehouse, \
                          user=op_user, ftaskinfo=TaskInfo.objects.get(name=name))
        AffirmInfo.objects.create(ip=obj[0]["hostsinfo__ip"], hosts_tags=dest_hosts_name, order_param=need_exce_param, \
                   releaser=op_user, release_status=2, ftaskinfo=TaskInfo.objects.get(name=name))
        code = "0"
        data["dest_net_status"] = code
        data["dest_file_status"] = code
        data["result_info"] = network_jduge_list
        data["id"] = ','.join(id_list)
        ed = time.time()
        print("-----spend--time-------", str(ed-st))
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "release/exce_task.html", data)
