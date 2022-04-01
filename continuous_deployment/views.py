from django.shortcuts import render

# Create your views here.

import json
import datetime
from pprint import pprint
from django.shortcuts import render,reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse,HttpResponseRedirect

from Ops.settings import TOKEN_INFO, GITLAB_URL, JEKINS_URL, USER_ID, TOKEN_ID
from user.views import user_privilges_info
from api.open_api import bash, dict_add_serial_number
from api.views import log_decor
from mirrors.mirror_api import GetDayTime
from django.db.models import Q

from .models import UserGitlabCommit, JenkinsBuild, UserGitlabConfigCommit
from .api import async_illegal_name_alert, async_run_pipeline, RemoteJekinsApi 


GT = GetDayTime()
SERVEN_DAY_AGO = GT.get_pre_later_time(-7, "%d/%m/%Y")
NOW_DAY = GT.get_pre_later_time(0, "%d/%m/%Y")
SEARCH_SERVEN_DAY_AGO = GT.get_pre_later_time(-7, "%Y-%m-%d")
SEARCH_NOW_DAY = GT.get_pre_later_time(1, "%Y-%m-%d")
 
#@login_required
@log_decor
def gitlab_commit_api(request):
    '''
    Post request is gitlab send a single to record the info by weebhook；
    :param request: 
    :return: 
    '''
    req_handle = request.POST
    print(req_handle)
    print(type(request.body))
    print("----request.body-------------",request.body)
    print("--------------gitlab_commit_list---------------")
    if request.method == "POST":
        body_content = json.loads(request.body)
        pprint(body_content)
        code_source =  body_content["ref"]
        event_name = body_content["event_name"]
        if code_source != "refs/heads/master" or event_name != "push":
            return JsonResponse({"data": "is not master branch to merge,cloudn't to build."}, status=200)
        commit_content = body_content["commits"][-1]["message"]
        if ';' in commit_content:
            version =  commit_content.replace("\n","").split(";")[-1]
            print("11111111111111%s-------------"%version)
            http_url = body_content["repository"]["git_http_url"]
            repository = body_content["project"]["name"]
            data = {"user_name":body_content["user_name"], "user_email":body_content["user_email"], \
                   "repository_name":repository, "git_http_url":http_url, "commit_id":body_content["after"], \
                   "commit_content":commit_content, "defined_version":version, "project_id":body_content["project_id"]}
            if UserGitlabCommit.objects.filter(commit_id=body_content["after"]).exists():
                print("-----errror----commit-id exit------", body_content["after"])
                return
            UserGitlabCommit.objects.create(**data)
            param_dict = {"repourl":http_url, "serviceName":repository, "commit_id":body_content["after"], "tag_name":version}
            print("---param_dict-----", param_dict)
            async_run_pipeline.delay("always_test_pipeline", param_dict, body_content["after"])
        else:
            name = body_content["user_name"]
            email = body_content["user_email"]
            alert_info = "%s 你好!%s工程命名不规范，请修正后重新提交"%(name, email)
            async_illegal_name_alert.delay(name, email, alert_info)
            data = {"user_name":name, "user_email":email, "repository_name":body_content["project"]["name"], \
                   "git_http_url":body_content["repository"]["git_http_url"], "project_id":body_content["project_id"], \
                   "commit_id":body_content["after"], "commit_content":commit_content}
            UserGitlabCommit.objects.create(**data)
        return JsonResponse({"data": ""}, status=200)

@login_required
@log_decor
def gitlab_commit_list(request):
    '''
    Get request is which show the commit info to web
    :param request: 
    :return: 
    '''
    data = {}
    if request.method == "GET":
        obj = UserGitlabCommit.objects.all().order_by("-creation_time")
        data["data"] = obj
        data["exit_priv"] = user_privilges_info(request)
        return render(request,'continuous_deployment/continuous_deployment.html',data)

@login_required
@log_decor
def retry_run_pipeline(request):
    '''
    when other reason lead to the pipeline run
    :param request:
    :return:
    '''
    if request.method == "POST":
        req_handle = request.POST
        retry_id_list = json.loads(req_handle.get("exce_id",""))
        retry_id = retry_id_list[0]
        obj = UserGitlabCommit.objects.filter(id=int(retry_id)).values("project_id", "defined_version", \
            "commit_id", "git_http_url", "repository_name")
        project_id = obj[0]["project_id"]
        version = obj[0]["defined_version"]
        http_url = obj[0]["git_http_url"]
        repository = obj[0]["repository_name"]
        commit_id = obj[0]["commit_id"]
        add_tag_info = "curl  -X POST -k -H 'PRIVATE-TOKEN: %s' '%s/api/v4/projects/%s/repository/tags?tag_name=%s&ref=master'" % (TOKEN_INFO, \
                       GITLAB_URL, project_id, version)
        param_dict = {"repourl": http_url, "serviceName": repository, "commit_id": commit_id}
        async_run_pipeline.delay("always_test_pipeline", param_dict, commit_id, add_tag_info)
#        return HttpResponseRedirect(reverse('cdeployment:buildlist'))
        ret_data = "/continuousd/jenkins_build_list/"
        return JsonResponse({"data": ret_data}, status=200)


@log_decor
def build_over_alert(request):
    '''
    the function is to alert by email or dingtalk when deployer commited formart error.
    :param request: 
    :return: 
    '''
    print("-----------build_over_alert--------------")
    if request.method == "POST":
        print(type(request.body))
        print(request.body)
        mid_var = request.body.decode("utf-8").replace("\n","")
        body_content = json.loads(mid_var)
        print("----body_content-----", body_content)
        unique_id = body_content["commit_id"]
        build_id = body_content["build_id"]
        code =  body_content["code"]
        respository =  body_content["respository"]
        print("commit_id-----", unique_id)
        print("build_id-----", build_id)
        print("code-----", code)
        print("respository-----", respository)
        print("respository-----", type(respository))
        NOW_DAY = GT.get_now_time("%Y-%m-%d %H:%M:%S")
        UserGitlabCommit.objects.filter(commit_id=unique_id).update(is_or_not_build=int(code))
        JenkinsBuild.objects.filter(build_number=build_id).update(build_status=int(code), update_time=NOW_DAY, harbor_mirror=respository)
        check_order = "curl  -X POST -k -H 'PRIVATE-TOKEN: %s' '%s/api/v4/projects/%s/repository/tags"
        return JsonResponse({"data": ""}, status=200)

@login_required
@log_decor
def jenkins_build_list(request):
    '''
    the fuction of jenkins_build_list is to show the info  about the history of builded.
    :param request:
    :return:
    '''
    data = {}
    if request.method == "GET":
        obj = JenkinsBuild.objects.values("pipeline_name", "build_number", "p_user_gitlab__repository_name", \
              "p_user_gitlab__defined_version", "build_status", "creation_time", "update_time").order_by("-creation_time")
        data["data"] = obj
        data["exit_priv"] = user_privilges_info(request)
        return render(request,'continuous_deployment/jenkins_build_list.html',data)

@login_required
@log_decor
def jenkins_build_detail(request):
    '''
    According to the number of build to show  the log.
    :param request:
    :return:
    '''
    data = {}
    if request.method == "GET":
        req_handle = request.GET
        build_no = req_handle.get("build_number", "")
        print("---build_no---%s--"%build_no)
        print(JenkinsBuild.objects.filter(build_number=int(build_no)).values("pipeline_name"))
        job_name = JenkinsBuild.objects.filter(build_number=int(build_no)).values("pipeline_name")[0]["pipeline_name"]
        req_handle = RemoteJekinsApi(JEKINS_URL, USER_ID, TOKEN_ID)
        log_data = req_handle.get_build_console_output(job_name, int(build_no))
        data["result_info"] = log_data
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'continuous_deployment/jenkins_build_detail.html', data)


def jenkins_build_sucessful_list(request):
    '''
    the fuction of jenkins_build_sucessful_list is to show the infomations about the history of sucessfully builded.
    :param request:
    :return:
    '''
    data = {}
    if request.method == "GET":
        data = {}
        data["start_time"] = SERVEN_DAY_AGO
        data["end_time"] = NOW_DAY
        data["exit_priv"] = user_privilges_info(request)
        obj = JenkinsBuild.objects.filter(Q(creation_time__range=(SEARCH_SERVEN_DAY_AGO, \
            SEARCH_NOW_DAY)) & Q(build_status=2)).values("id", "p_user_gitlab__repository_name", \
            "p_user_gitlab__defined_version", "creation_time", "update_time")
        data['data'] = obj
        return render(request, 'continuous_deployment/jenkins_build_sucessful_list.html', data)
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
        obj = JenkinsBuild.objects.filter(Q(creation_time__range=(st_time, \
            ed_time)) & Q(build_status=2)).values("id", "p_user_gitlab__repository_name", \
            "p_user_gitlab__defined_version", "creation_time", "update_time")
        data['data'] = obj
        return  render(request, 'continuous_deployment/jenkins_build_sucessful_list.html', data)


@log_decor
def gitlab_config_commit_api(request):
    '''
    Post request is gitlab send a single to record the info by weebhook；
    :param request:
    :return:
    '''
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    print("-----------ip------------", ip)

    req_handle = request.POST
    print(req_handle)
    print(type(request.body))
    print("----request.body-------------", request.body)
    if request.method == "POST":
        body_content = json.loads(request.body)
        pprint(body_content)
        code_source = body_content["ref"]
        event_name = body_content["event_name"]
    #    if code_source != "refs/heads/master" or event_name != "push":
     #       return JsonResponse({"data": "is not master branch."}, status=200)
        commit_content = body_content["commits"][-1]["message"]
        name = body_content["user_name"]
        email = body_content["user_email"]
        data = {"edit_user": name, "user_email": email, "repository_name": body_content["project"]["name"], \
                "git_http_url": body_content["repository"]["git_http_url"],  \
                "commit_id": body_content["after"], "commit_content": commit_content}
        UserGitlabConfigCommit.objects.create(**data)
    return JsonResponse({"data": "sucessful recorded the commit of edited config"}, status=200)


@login_required
@log_decor
def gitlab_config_commit(request):
    '''
    Get request is which show the config commit info to web
    :param request:
    :return:
    '''
    data = {}
    if request.method == "GET":
        obj = UserGitlabConfigCommit.objects.values("id", "edit_user", "user_email", "repository_name", \
              "git_http_url", "commit_id", "commit_content", "creation_time").order_by("-creation_time")
        data["data"] = dict_add_serial_number(obj)
        data["exit_priv"] = user_privilges_info(request)
        return render(request,'continuous_deployment/gitlab_config_list.html',data)

