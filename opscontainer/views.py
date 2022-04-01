
# Create your views here.

import os
import time
import copy
import json
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count
from release.models import HostsInfo
from user.views import user_privilges_info
from api.open_api import bash, write_file
from api.views import log_decor
from release.views import code_trans_lang
from release.release_api import DockerRemoteApi
from .models import ContainerDist, HostUnit, ContainerEnv, ContainerEnvGroup
from mirrors.mirror_api import GetDayTime



@login_required
@permission_required('opscontainer.scanf_containerdist')
@log_decor
def host_unit_list(request):
    if request.method == "GET":
        data = {}
        data["exit_priv"] = user_privilges_info(request)
        exit_data = HostUnit.objects.values("id", "name", "add_user", "host_tag", "creation_time", \
                                               "update_time").order_by("update_time")
        for  i  in exit_data:
            host_tag_list = i["host_tag"].split(',')
            i["host_tag"] = host_tag_list
        data["data"] = code_trans_lang(exit_data)
        data["exit_container"] = []
        tree_dict = {}
        tree_one_list = []
        docker_handle = DockerRemoteApi()
        env_obj = ContainerEnvGroup.objects.filter(name="uat-1-环境组").values("relation_env__name").distinct()
        print("----name-----", env_obj)
        for mid_obj in env_obj:
            mid_dict = {}
            mid_tree_list = []
            mid_name = mid_obj["relation_env__name"]
            mid_list = ContainerEnv.objects.filter(name=mid_name).values("relation_hostinfo__name", "relation_hostinfo__ip")
            for last_obj in mid_list:
                one_data_dict = docker_handle.get_container_tree_data(last_obj["relation_hostinfo__ip"], last_obj["relation_hostinfo__name"])
                mid_tree_list.append(one_data_dict)
            mid_dict.update({"name":mid_name, "children":mid_tree_list})
            tree_one_list.append(mid_dict)
        tree_dict.update({"name":"uat-1-环境组", "children":tree_one_list})
        json_data = json.dumps(tree_dict)
        os.remove("/opsenv/Ops/static/data/flare.json")
        write_file(json_data, "/opsenv/Ops/static/data/flare.json")
        return render(request, 'opscontainer/host_unit_list.html', data)

@login_required
@permission_required('opscontainer.add_containerdist')
@log_decor
def add_host_unit(request):
    data = {}
    if request.method == "POST":
        rep_handle = request.POST
        gname = rep_handle.get("name")
        ghost_tag = rep_handle.getlist("ip")
        ghost_tag = ','.join(ghost_tag)
        user = request.user
        HostUnit.objects.create(name=gname, host_tag=ghost_tag, add_user=user)
        return HttpResponseRedirect(reverse('opscont:hostunit'))
    else:
        hostinfo = HostsInfo.objects.values("name", "ip")
        data["ips"] = hostinfo
        data["exit_priv"] = user_privilges_info(request)
        return  render(request, 'opscontainer/add_host_unit.html', data)

@login_required
@permission_required('opscontainer.delete_containerdist')
@log_decor
def del_host_unit(request):
    if request.method == "GET":
        rep_handle = request.GET
        id = rep_handle["del_id"]
        print("----------------id---------", id)
        HostUnit.objects.filter(id=id).delete()
        return HttpResponseRedirect(reverse('opscont:hostunit'))


@login_required
@permission_required('opscontainer.change_containerdist')
@log_decor
def edit_host_unit(request):
    if request.method == "POST":
        rep_handle = request.POST
        edit_user = str(request.user)
        gname = rep_handle["gname"]
        ghost_tag = rep_handle.getlist("ip")
        ghost_tag = ','.join(ghost_tag)
        gid = int(rep_handle["id"])
        HostUnit.objects.filter(id=gid).update(name=gname, host_tag=ghost_tag, add_user=edit_user)
        return HttpResponseRedirect(reverse('opscont:hostunit'))
    else:
        data = {}
        rep_handle = request.GET
        id = rep_handle["edit_id"]
        host_unit_name = HostUnit.objects.filter(id=id).values("id", "name")
        host_unit_info = HostUnit.objects.filter(id=id).values("host_tag")
        hosts_info = list(HostsInfo.objects.all().values("ip", "name"))
        mid_hosts_info = copy.deepcopy(hosts_info)
        ips = host_unit_info[0]["host_tag"].split(",")
        for  i  in mid_hosts_info:
            for o in ips:
                mid = i["ip"]+':'+i["name"]
                if o == mid:
                    hosts_info.remove(i)

        data["exit_hosts_info"] = host_unit_info[0]["host_tag"].split(",")
        data["group_name"] = host_unit_name[0]["name"]
        data["all_host_info"] = hosts_info
        data["exit_priv"] = user_privilges_info(request)
        data["id"] = host_unit_name[0]["id"]
        return render(request, 'opscontainer/edit_host_unit.html', data)


@login_required
@permission_required('opscontainer.scanf_containerdist')
@log_decor
def get_container_by_group(request):
    if request.method == "GET":
        data = {}
        req_handle = request.GET
        gid = req_handle["gid"]
        host_tag = HostUnit.objects.filter(id=gid).values("host_tag", "name")
        gname = host_tag[0]["name"]
        host_tag_str = host_tag[0]["host_tag"]
        host_tag_list = host_tag_str.split(',')
        exit_container_dict = {}
        dict_key_list = []
        for i in host_tag_list:
            host_name = i.split(":")[1]
            bash_order = "ansible %s -m command -a \"docker ps\"|awk -F \" \" '{print  $2}'|\
                         grep  -v \"ID\"|grep -v \"|\""%(host_name)
            values = bash(bash_order)
            print("-------values-----", values)
            print("-------values-----", bash_order)
            list_values = values.split("\n")
            dict_key_list.append(list_values)
        exit_container_dict.update({gname:dict_key_list})
        data["exit_priv"] = user_privilges_info(request)
        exit_data = HostUnit.objects.values("id", "name", "add_user", "host_tag", "creation_time",\
                                               "update_time").order_by("update_time")
        for  i  in exit_data:
            host_tag_list = i["host_tag"].split(',')
            i["host_tag"] = host_tag_list
        data["data"] = exit_data
        data["exit_container"] = exit_container_dict
        return render(request, 'opscontainer/host_unit_list.html', data)


@login_required
@permission_required('opscontainer.scanf_containerenv')
@log_decor
def container_env_list(request):
    data = {}
    if request.method == 'POST':
        pass
    else:
        single_flag = ContainerEnv.objects.order_by("-creation_time").values("unique_flag", "relation_hostinfo__ip")
        print("------------in----container_env_list---")
        data["obj_count"] = ContainerEnv.objects.values("unique_flag").annotate(times=Count("unique_flag"))
        print("------------data-obj_count--", data)
        obj = code_trans_lang(ContainerEnv.objects.values("name", "unique_flag", "relation_hostinfo__name", \
                       "relation_hostinfo__ip", "create_user", "creation_time", "update_time"))
        data["data"] = obj
        single_flag_dict = {}
        single_flag_list = []
        for mid in single_flag:
            single_flag_dict.update({mid["unique_flag"]:mid["relation_hostinfo__ip"]})
        for key, value in single_flag_dict.items():
            single_flag_result_dict = {}
            single_flag_result_dict.update({"unique_flag":key})
            single_flag_result_dict.update({"relation_hostinfo_ip":value})
            single_flag_list.append(single_flag_result_dict)
        data["single_flag"] = single_flag_list
        print("---------single_flag_list---", single_flag_list)
        data["exit_priv"] = user_privilges_info(request)
        print("-----------1111111111111---------")
        return render(request, "opscontainer/container_env_list.html", data)

@login_required
@permission_required('opscontainer.add_containerenv')
@log_decor
def add_container_env(request):
    data = {}
    if request.method == 'POST':
        req_handler = request.POST
        unique_flag = str(time.time()).replace(".","")
        name = req_handler["function_name"]
        hosts_info_list = req_handler.getlist("host_flag")
        data["exit_priv"] = user_privilges_info(request)
        if ContainerEnv.objects.filter(name=name).exists():
            data["error"] = "用户名已存在,请重新输入!"
            return render(request, "opscontainer/add_container_env.html", data)
        for hosts_info in hosts_info_list:
            hosts_ip = hosts_info.split(":")[1]
            hostsinfo_obj = HostsInfo.objects.get(ip=hosts_ip)
            ContainerEnv.objects.create(unique_flag=unique_flag, relation_hostinfo=hostsinfo_obj, \
                        create_user=request.user, name=name)
        return HttpResponseRedirect(reverse('opscont:envlist'))
    else:
        data["flag_value"] = "False"
        data["exit_priv"] = user_privilges_info(request)
        data["data"] = HostsInfo.objects.values("ip", "name")
        return render(request, "opscontainer/add_container_env.html", data)

@login_required
@permission_required('opscontainer.delete_containerenv')
@log_decor
def del_container_env(request):
    if request.method == 'POST':
        req_handler = request.POST
        tags = json.loads(req_handler["tag"])
        ContainerEnv.objects.filter(unique_flag=tags).delete()
        return JsonResponse({"ret": "sucessful","data":"/container/container_env_list"}, status=200,)

@login_required
@permission_required('opscontainer.change_containerenv')
@log_decor
def edit_container_env(request):
    data = {}
    if request.method == 'GET':
        req_handler = request.GET
        tags = req_handler["tag"]
        obj = ContainerEnv.objects.filter(unique_flag=tags).values("name", "relation_hostinfo__ip", \
                    "relation_hostinfo__name")
        host_info_obj = HostsInfo.objects.values("ip", "name")
        ip_list = []
        locked_hostinfo_list = []
        for mid in obj:
            ip_list.append(mid["relation_hostinfo__ip"])
        for mid_hosts in  host_info_obj:
            for mid_ip in ip_list:
                if mid_hosts["ip"] == mid_ip:
                    locked_hostinfo_list.append(mid_hosts)
        unlock_hostinfo_list = [i for i in host_info_obj if i not in locked_hostinfo_list]
        data["flag_value"] = "True"
        data["name"] = obj[0]["name"]
        data["locked_list"] = locked_hostinfo_list
        data["unlocked_list"] = unlock_hostinfo_list
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opscontainer/add_container_env.html", data)
    else:
        GT = GetDayTime()
        NOW_DAY = GT.get_now_time("%Y-%m-%d %H:%M:%S")
        req_handler = request.POST
        name = req_handler["function_name"]
        hosts_info_list = req_handler.getlist("host_flag")
        hostinfo_ip_list = []
        for i in hosts_info_list:
            hostinfo_ip_list.append(i.split(":")[1])
        unique_flag = ContainerEnv.objects.filter(name=name).values("unique_flag")[0]["unique_flag"]
        hostinfo_ips = ContainerEnv.objects.filter(name=name).values("relation_hostinfo__ip")
        for mid_host_info in hostinfo_ips:
            if mid_host_info["relation_hostinfo__ip"] not in hostinfo_ip_list:
                ContainerEnv.objects.filter(relation_hostinfo__ip=mid_host_info["relation_hostinfo__ip"], name=name).delete()
        for hosts_info in hosts_info_list:
            hosts_ip = hosts_info.split(":")[1]
            hostsinfo_obj = HostsInfo.objects.get(ip=hosts_ip)
            if ContainerEnv.objects.filter(name=name, relation_hostinfo=hostsinfo_obj).exists():
                ContainerEnv.objects.filter(name=name, relation_hostinfo=hostsinfo_obj).update(update_time=NOW_DAY)
            else:
                ContainerEnv.objects.create(unique_flag=unique_flag, relation_hostinfo=hostsinfo_obj, \
                        create_user=request.user, name=name)
        data["exit_priv"] = user_privilges_info(request)
        return HttpResponseRedirect(reverse('opscont:envlist'))

@login_required
@permission_required('opscontainer.scanf_containerenvgroup')
@log_decor
def container_env_group(request):
    data = {}
    if request.method == 'GET':
        print("------------container_env_group------in----")
        single_flag = ContainerEnvGroup.objects.order_by("-creation_time").values("unique_flag", \
                     "relation_env__name", "relation_env__id")
        print("------------single_flag----------", single_flag)
        obj_count = ContainerEnvGroup.objects.values("unique_flag").annotate(times=Count("unique_flag"))
        print("------------obj_count----------", obj_count)
        data["obj_count"] = obj_count
        obj = code_trans_lang(ContainerEnvGroup.objects.values("name", "unique_flag", "relation_env__name", \
                       "relation_env__id", "create_user", "creation_time", "update_time"))
        print("------------obj----",obj)
        data["data"] = obj
        hostinfo_dict = {}
        for mid_obj in single_flag:
            hostinfo_dict.update({mid_obj["relation_env__name"]:mid_obj["relation_env__id"]})
        single_flag_dict = {}
        single_flag_list = []
        for mid in single_flag:
            single_flag_dict.update({mid["unique_flag"]:[mid["relation_env__name"], mid["relation_env__id"]]})
        for key, value in single_flag_dict.items():
            single_flag_result_dict = {}
            single_flag_result_dict.update({"unique_flag":key})
            single_flag_result_dict.update({"relation_env_name":value[0]})
            single_flag_result_dict.update({"relation_env_id":value[1]})
            single_flag_list.append(single_flag_result_dict)
        ret_env_name_list = []
        for key, value in hostinfo_dict.items():
            mid_env_name_dict = {}
            mid_env_name_dict.update({"name":key})
            mid_env_name_dict.update({"id":value})
            ret_env_name_list.append(mid_env_name_dict)
        data["single_flag"] = single_flag_list
        data["env_name_times"] = ret_env_name_list 
        data["hostinfo_dict"] = hostinfo_dict
        print("---------single_flag_list---", single_flag_list)
        data["exit_priv"] = user_privilges_info(request)
        print("-----------ret_env_name_list---------", ret_env_name_list)
        print("-----------1111111111111---------")
        return render(request, "opscontainer/container_env_group_list.html", data)


@login_required
@permission_required('opscontainer.add_containerenvgroup')
@log_decor
def add_container_env_group(request):
    data = {}
    if request.method == 'POST':
        req_handler = request.POST
        unique_flag = str(time.time()).replace(".","")
        name = req_handler["function_name"]
        env_info_list = req_handler.getlist("env_flag")
        data["exit_priv"] = user_privilges_info(request)
        if ContainerEnvGroup.objects.filter(name=name).exists():
            data["error"] = "用户名已存在,请重新输入!"
            return render(request, "opscontainer/add_container_env_group.html", data)
        for mid_name in env_info_list:
            env_obj = ContainerEnv.objects.filter(name=mid_name).values("id")
            for env_id in env_obj:
                single_env_obj = ContainerEnv.objects.get(pk=env_id["id"])
                ContainerEnvGroup.objects.create(unique_flag=unique_flag, relation_env=single_env_obj, \
                              name=name, create_user=request.user)
        return HttpResponseRedirect(reverse('opscont:genvlist')) 
    else:
        data["flag_value"] = "False"
        data["exit_priv"] = user_privilges_info(request)
        data["data"] = ContainerEnv.objects.values("name").distinct()
        return render(request, "opscontainer/add_container_env_group.html", data)

@login_required
@permission_required('opscontainer.delete_containerenvgroup')
@log_decor
def del_container_env_group(request):
    if request.method == 'POST':
        req_handler = request.POST
        tags = json.loads(req_handler["tag"])
        ContainerEnvGroup.objects.filter(unique_flag=tags).delete()
        return JsonResponse({"ret": "sucessful","data":"/container/container_env_group/"}, status=200,)

@login_required
@permission_required('opscontainer.change_containerenvgroup')
@log_decor
def edit_container_group_env(request):
    data = {}
    if request.method == 'GET':
        req_handler = request.GET
        tags = req_handler["tag"]
        obj = ContainerEnvGroup.objects.filter(unique_flag=tags).values("name", "relation_env__name").distinct()
        container_info_obj = ContainerEnv.objects.values("name").distinct()
        locked_hostinfo_list = []
        name_list = []
        for mid in obj:
            name_list.append(mid["relation_env__name"])
        for mid_hosts in container_info_obj:
            for mid_name in name_list:
                if mid_hosts["name"] == mid_name:
                    locked_hostinfo_list.append(mid_hosts)
        unlock_hostinfo_list = [i for i in container_info_obj if i not in locked_hostinfo_list]
        data["flag_value"] = "True"
        data["name"] = obj[0]["name"]
        data["locked_list"] = locked_hostinfo_list
        data["unlocked_list"] = unlock_hostinfo_list
        data["exit_priv"] = user_privilges_info(request)
        return render(request, "opscontainer/add_container_env_group.html", data)
    else:
        GT = GetDayTime()
        NOW_DAY = GT.get_now_time("%Y-%m-%d %H:%M:%S")
        req_handler = request.POST
        name = req_handler["function_name"]
        container_name_list = req_handler.getlist("env_flag")
        print("----------container_name_list----------", container_name_list, type(container_name_list))
        container_info_obj = ContainerEnv.objects.values("name").distinct()
        print("-------container_info_obj-----", container_info_obj)
        unique_flag = ContainerEnvGroup.objects.filter(name=name).values("unique_flag")[0]["unique_flag"]
        exit_container_name = ContainerEnvGroup.objects.filter(unique_flag=unique_flag).values("relation_env__name").distinct()
        print("-------exit_container_name-----", exit_container_name)
        for exit_container in exit_container_name:
            if exit_container["relation_env__name"] not in container_name_list:
                print("-------8888---exit_container--", exit_container["relation_env__name"], "------exit_container[\"relation_env__name\"]-------",exit_container["relation_env__name"])
                ContainerEnvGroup.objects.filter(name=name, relation_env__name=exit_container["relation_env__name"]).delete()
        for container in container_name_list:
            print("------666666666--container---", container)
            container_single_obj = ContainerEnvGroup.objects.filter(relation_env__name=container).values("relation_env__id")
            print("------777777-------", container_single_obj)
            for ids in container_single_obj:
                container_obj = ContainerEnv.objects.get(id=ids["relation_env__id"])
                if ContainerEnvGroup.objects.filter(name=name, relation_env__name=container).exists():
                    print("---1111111111111---exit---")
                    ContainerEnvGroup.objects.filter(name=name, relation_env__name=container).update(update_time=NOW_DAY)
                else:
                    print("-1111111111111-not----exit---", container_obj)
                    ContainerEnvGroup.objects.create(unique_flag=unique_flag, relation_env=container_obj, \
                                 name=name, create_user=request.user)
                    print("-1111111111111-not----exit-ed--",ContainerEnvGroup.objects.filter(unique_flag=unique_flag).all())
        print("------rnd---")
        data["exit_priv"] = user_privilges_info(request)
        return HttpResponseRedirect(reverse('opscont:genvlist'))
