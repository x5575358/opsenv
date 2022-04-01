# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/2 13:36
# File  : views.py
# Software PyCharm

from user.views import user_privilges_info
from opslog.models import LoginRecorder
from asset.models import Ec2AssetInfo, RegionName, ElbLoadBalancers, RdsBasicInfo
from release.models import TaskInfo
from mchange.models import ChangeRecorder
from mirrors.models import ProjectInfo, MirrorWarehouse
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum

from opslog.log_api import  logger
from celery_demo.tasks import release_exec 
from  .dbinit import Setup
from api.views import log_decor
from mirrors.mirror_api import GetDayTime


GT = GetDayTime()
now_day = GT.get_pre_later_time(1,"%Y-%m-%d")
serven_day = GT.get_pre_later_time(-7,"%Y-%m-%d")

def get_five_user_data(vistor_data):
    mid_list = []
    date_list = []
    for pos in range(5):
        tmp_dict = {}
        if pos + 1 > len(vistor_data):
            continue
        tmp_list = []
        vistor_user_name = vistor_data[pos]["user_name"]
        for in_pos in range(6,-1,-1):
            st_day = GT.get_pre_later_time(-in_pos, "%Y-%m-%d")
            if pos == 0:
                date_list.append(st_day)

            obj = LoginRecorder.objects.filter(Q(creation_time__icontains=st_day) & Q(user_name=vistor_user_name)\
                  ).values("user_name").annotate(times=Count('user_name')).order_by('-times')
            if obj:
                tmp_list.append(obj[0].get("times"))
            else:
                tmp_list.append(0)
        tmp_dict.update({vistor_user_name:tmp_list})
        mid_list.append(tmp_dict)
    return date_list, mid_list


'''
login_required是一个快捷函数,作用是当前用户未认证的话直接返回到
login_url?redirect_field_name页面下,将前面两个参数换成对应的值即"/"页面下
'''
@login_required(redirect_field_name='', login_url='/')
@log_decor
def index(request):
    data = {}
    data["exit_priv"] = user_privilges_info(request)
    data["project_count"] = ProjectInfo.objects.all().count()
    data["warehous_count"] = ProjectInfo.objects.aggregate(Sum("repo_count"))
    data["tags_count"] = MirrorWarehouse.objects.aggregate(Sum("tags_count"))
    print("-------data[\"exit_priv\"]-------", data["exit_priv"])
    print("-------data[\"project_count\"]-------", data["project_count"])
    print("------- data[\"tags_count\"]-------",  data["tags_count"])
    vistor_serven_day = LoginRecorder.objects.filter(creation_time__range=(serven_day, \
                  now_day)).values("user_name").annotate(times=Count('user_name')).order_by('-times')
    x_axis, y_list= get_five_user_data(vistor_serven_day)
    y_axis_list = []
    for y_dict in y_list:
        for key, value in y_dict.items():
            y_axis_list.append({"name":key, "data":value})
    data["x_axis"] = x_axis
    data["y_axis"] = y_axis_list
    print("-------x_axis-------", x_axis)
    print("-------y_axis-------", y_axis_list)

    resource_data_count = []
    region_name_obj = RegionName.objects.values("name", "code")
    for mid_region in region_name_obj:
        region_name = mid_region["name"]
        ec2_mid_list = []
        ec2_count = Ec2AssetInfo.objects.filter(availability_zone__startswith=mid_region["code"]).filter(~Q(update_status=9)).count()
        alb_count = ElbLoadBalancers.objects.filter(attribution_area__code=mid_region["code"]).filter(~Q(update_status=9)).count()
        rds_count = RdsBasicInfo.objects.filter(attribution_area__code=mid_region["code"]).filter(~Q(update_status=9)).count()
        ec2_mid_list.append(ec2_count)
        ec2_mid_list.append(alb_count)
        ec2_mid_list.append(rds_count)
        try:
            ec2_mid_dict = {"name": region_name, "data":ec2_mid_list}
        except MemoryError as er:
            print("----error-----", er)
        except Exception as e:
            print("------e------",e)
        resource_data_count.append(ec2_mid_dict)
    data["resource_data_count"] = bubble_sort(resource_data_count)
    print("------data[\"resource_data_count\"]-----=", bubble_sort(resource_data_count))
    ec2_type_obj = Ec2AssetInfo.objects.filter(~Q(update_status=9)).values("instance_type").annotate(times=Count('instance_type')).order_by("-times")
    ec2_type_data_list = []
    ec2_picture_data = []
    for pos in range(len(ec2_type_obj)):
        if pos < 10:
            mid_type = ec2_type_obj[pos]
        else:
            break
        mid_count_list = []
        mid_count_list.append(mid_type["times"])
        ec2_type_data = {"name": mid_type["instance_type"], "data":mid_count_list}
        ec2_type_data_list.append(ec2_type_data)
        mid_data_dict = {"name":mid_type["instance_type"], "y":mid_type["times"]}
        ec2_picture_data.append(mid_data_dict)
    data["ec2_type_data_list"] = ec2_type_data_list
    data["ec2_picture_data"] = ec2_picture_data
    print("----------- data[\"ec2_picture_data\"]----=", ec2_type_data_list) 
    ec2_env_obj = Ec2AssetInfo.objects.filter(~Q(update_status=9)).values("define_instance_tag").annotate(times=Count('define_instance_tag'))
    ec2_env_list = []
    for mid_ec2_env in ec2_env_obj:
        if 0 == len(ec2_env_list):
            ec2_env_list.append({"name":mid_ec2_env["define_instance_tag"], "y":int(mid_ec2_env["times"]), \
                "sliced":"true", "selected":"true"})
        else:
            ec2_env_list.append({"name":mid_ec2_env["define_instance_tag"], "y":int(mid_ec2_env["times"])})
    print("-----ec2_env_list-----", ec2_env_list)
    data["ec2_env_list"] = ec2_env_list
    logger.debug(str(request.user)+" by the "+str(request.method)+\
           "  way to request the page of index.html ")
    return render(request, 'index.html', data)


def bubble_sort(src_list):
    print("--in-src_list---", src_list)
    src_len = len(src_list)
    for out_pos in range(src_len):
        for inner_pos in range(src_len):
            if src_list[out_pos]["data"][0] < src_list[inner_pos]["data"][0]:
                mid_value = src_list[inner_pos]
                src_list[inner_pos] = src_list[out_pos]
                src_list[out_pos] = mid_value
    print("---src_list---", src_list)
    return src_list

