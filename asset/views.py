# Create your views here.
from django.shortcuts import render, reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from django.http import  HttpResponse,HttpResponseRedirect,FileResponse
from django.utils.encoding import escape_uri_path

from django.db.models import Q, Avg

from .create_ec2_tag import auto_create_tag, auto_delete_tag
from .asset_api  import *
from .aws_server_instance_price_used_condition import InstanceReportGenerator
import boto3
import os
import json
import datetime
from .models import Ec2AssetInfo, RegionName, Ec2CpuNetworkHistoryData
from user.views import user_privilges_info
from api.views import log_decor
from release.views import code_trans_lang 
from opslog.log_api import  logger
from Ops.settings import EC2_USED_CONDITION_DIR
from mirrors.mirror_api import GetDayTime


GT = GetDayTime()

@login_required
@permission_required('asset.scanf_ec2')
@log_decor
def asset_list(request):
    '''
    invoking the get way to list the info about the ec2 info
    invoking the post way to list the ec2 info according the provided conditions
    :param request:
    :return: the ec2 info
    '''
    data = {}
    if request.method == 'GET':
        SERVEN_DAY_AGO = GT.get_pre_later_time(-7, "%Y-%m-%d")
        NOW_DAY = GT.get_now_time("%Y-%m-%d")
#        auto_delete_tag()
#        auto_create_tag()
#        ec2_network_cpu_used_condition()
  #      print("SERVEN_DAY_AGO=======", SERVEN_DAY_AGO, "NOW_DAY======",NOW_DAY)
   #     obj = Ec2CpuNetworkHistoryData.objects.filter(detail_day__range=(SERVEN_DAY_AGO, NOW_DAY)).values('ec2_instance_f__id', "detail_day")
 #       obj = Ec2CpuNetworkHistoryData.objects.filter(detail_day__range=(SERVEN_DAY_AGO, NOW_DAY)).values(\
  #      'ec2_instance_f__instance_name', "ec2_instance_f__instance_type").annotate(\
  #      Avg("cpu_utilization"), Avg("network_in"), Avg("network_out"))
  #      print("-----obj-------", obj)
        data["selected_data"] = ""
        data["region_data"] = RegionName.objects.values("name")
        data["selected_data"] = ""
        data["exit_priv"] = user_privilges_info(request)
        data['data'] = code_trans_lang(scanf_asset_basic_info())
        return render(request,'asset/asset_list.html',data)
    else:
        req_handle = request.POST
        region_name = req_handle.get("env_flag", "")
        if region_name is None or region_name == "":
            return HttpResponseRedirect(reverse('asset:ec2infolist')) 
        else:
            region_obj = RegionName.objects.filter(name=region_name).values("code")
            region_code = region_obj[0]["code"]
            data['data'] = code_trans_lang(Ec2AssetInfo.objects.filter(availability_zone__startswith=region_code).values("instance_id", \
                            "instance_name", "public_ip", "private_ip", "disk_count", "disk_size", "memory_size", "define_instance_tag",\
                            "core_count", "instance_type", "instance_status", "create_time", "availability_zone", "instance_key_word"))
            data["selected_data"] = region_name
            data["region_data"] = RegionName.objects.filter(~Q(name=region_name)).values("name")
        data["exit_priv"] = user_privilges_info(request)
        return render(request,'asset/asset_list.html',data)


def get_disk_info(ec2_hander,src):
    disk_count = 0
    disk_size = 0
    for o in src:
        v = ec2_hander.Volume('%s'%o["Ebs"]["VolumeId"])
        disk_size=disk_size+v.size
        disk_count = disk_count+1
    return disk_count,disk_size

def get_ec2_info():
    print("---st----get_ec2_info----")
    data={}
    region_name_list = RegionName.objects.all().values_list("code")
    Ec2AssetInfo.objects.filter(~Q(update_status=9)).update(update_status=0)
    now_time = GT.get_now_time("%Y-%m-%d %H:%M:%S")
    for r in region_name_list:
        r=r[0]
        ec2 = boto3.resource('ec2', region_name=r)
        instances = ec2.instances.all()
        for instance in instances:
            mid_var = instance.block_device_mappings
            disk_count,disk_size = get_disk_info(ec2,mid_var)
            cpu_info = instance.cpu_options
            availability_zone = instance.placement["AvailabilityZone"]
            if instance.public_ip_address is None:
                ip = ""
            else:
                ip = instance.public_ip_address
            if instance.private_ip_address is None:
                #Ec2AssetInfo.objects.filter(instance_id=instance.id).delete()
                Ec2AssetInfo.objects.filter(instance_id=instance.id).update(update_status=9, delete_time=now_time)
                continue
            instance_name = ""
            def_instance_tag = ""
            for mid_name in instance.tags:
                if mid_name["Key"] == "Name":
                    instance_name = mid_name["Value"]
                if mid_name["Key"] == "UsageEnvironment":
                    def_instance_tag = mid_name["Value"]
            data.update(dict({"instance_id":instance.id, "instance_name":instance_name,\
                 "public_ip":ip, "instance_type":instance.instance_type, \
                 "private_ip":instance.private_ip_address, "availability_zone":availability_zone, \
                 "disk_count":disk_count, "disk_size":disk_size, "define_instance_tag":def_instance_tag,\
                 "memory_size":cpu_info["CoreCount"], "core_count":cpu_info["ThreadsPerCore"], \
                 "instance_status":instance.state["Name"], "create_time":instance.launch_time, \
                 "update_status":1, "instance_key_word":instance.key_name}))
            isornotexit = Ec2AssetInfo.objects.filter(instance_id=instance.id).exists()
            if isornotexit:
                Ec2AssetInfo.objects.filter(instance_id=instance.id).update(**data)
            else:
                Ec2AssetInfo.objects.create(**data)
    print("---ed----get_ec2_info----")
    Ec2AssetInfo.objects.filter(update_status=0).update(update_status=9, delete_time=now_time)

@login_required
@permission_required('asset.scanf_elbloadbalancers')
@log_decor
def show_alb_info(request):
    '''
    show the info of alb
    :param request:
    :return: alb basic info obj
    '''
    data = {}
    if request.method == 'GET':
        data["selected_data"] = ""
        data["region_data"] = RegionName.objects.values("name")
        data["selected_data"] = ""
        data["exit_priv"] = user_privilges_info(request)
        data['data'] = code_trans_lang(ElbLoadBalancers.objects.values("id", \
                            "availability_zones", "dns_name", "ip_address_types", "security_groups", \
                            "load_balancer_name", "scheme", "state", "types", "vpc_id", "create_time",\
                            "attribution_area__name"))
        return render(request,'asset/show_alb_basic_info.html',data)
    else:
        print("---post----show_alb_info----")
        req_handle = request.POST
        region_name = req_handle.get("env_flag", "")
        if region_name is None or region_name == "":
            return HttpResponseRedirect(reverse('asset:albinfolist'))
        else:
            data['data'] = code_trans_lang(ElbLoadBalancers.objects.filter(attribution_area__name=region_name).values("id", \
                            "availability_zones", "dns_name", "ip_address_types", "security_groups", \
                            "load_balancer_name", "scheme", "state", "types", "vpc_id", "create_time",\
                            "attribution_area__name"))
            data["selected_data"] = region_name
            data["region_data"] = RegionName.objects.filter(~Q(name=region_name)).values("name")
        data["exit_priv"] = user_privilges_info(request)
        return render(request,'asset/show_alb_basic_info.html',data)

@login_required
@permission_required('asset.scanf_rdsbasicinfo')
@log_decor
def show_rds_info(request):
    '''
    show the info of rds
    :param request:
    :return: rds basic info obj
    '''
    data = {}
    if request.method == 'GET':
        data["selected_data"] = ""
        data["region_data"] = RegionName.objects.values("name")
        data["selected_data"] = ""
        data["exit_priv"] = user_privilges_info(request)
        data['data'] = code_trans_lang(RdsBasicInfo.objects.values("id", "db_instance_class",\
                            "db_name", "endpoint_address", "engine", "engine_version", \
                            "allocated_storage", "db_instance_status", "endpoint_port", "create_time", \
                            "attribution_area__name"))
        return render(request,'asset/show_rds_basic_info.html',data)
    else:
        req_handle = request.POST
        region_name = req_handle.get("env_flag", "")
        if region_name is None or region_name == "":
            return HttpResponseRedirect(reverse('asset:rdsinfolist'))
        else:
            region_obj = RegionName.objects.filter(name=region_name).values("code")
            region_code = region_obj[0]["code"]
            data['data'] = code_trans_lang(RdsBasicInfo.objects.filter(attribution_area__code=region_code).values("id", \
                            "db_name", "endpoint_address", "engine", "engine_version", "db_instance_class" ,\
                            "allocated_storage", "db_instance_status", "endpoint_port", "create_time", \
                            "attribution_area__name"))
            data["selected_data"] = region_name
            data["region_data"] = RegionName.objects.filter(~Q(name=region_name)).values("name")
        data["exit_priv"] = user_privilges_info(request)
        return render(request,'asset/show_rds_basic_info.html',data)


def aws_interface_get_elb_info():
    '''
    To get the basic infomations of elb by invoking the interface of the aws boto3
    :return:
    '''
    region_name_list = RegionName.objects.all().values_list("code")
    ElbLoadBalancers.objects.all().update(update_status=0)
    for r in region_name_list:
        r = r[0]
        region_obj = RegionName.objects.get(code=r)
        client = boto3.client('elbv2', region_name=r)
        obj = client.describe_load_balancers()
        elb_obj_list = obj["LoadBalancers"]
        for elb_obj in elb_obj_list:
            arn = elb_obj["LoadBalancerArn"]
            mid_zone_list = []
            for mid_zones in elb_obj["AvailabilityZones"]:
                mid_zone_list.append(mid_zones["ZoneName"])
            mid_zone_str = ','.join(mid_zone_list)
            data = {"availability_zones":mid_zone_str, "update_status":1 , \
                    "canonical_hosted_zone_id":elb_obj["CanonicalHostedZoneId"], "dns_name":elb_obj["DNSName"], \
                    "create_time":elb_obj["CreatedTime"], "ip_address_types":elb_obj["IpAddressType"], \
                    "load_balancer_arn":arn, "scheme":elb_obj["Scheme"], \
                    "load_balancer_name":elb_obj["LoadBalancerName"], "state":elb_obj["State"]["Code"], \
                    "security_groups":elb_obj["SecurityGroups"], "types":elb_obj["Type"], \
                    "vpc_id":elb_obj["VpcId"], "attribution_area":region_obj, "update_status":1}
            from pprint import pprint
            print("----data-----")
            pprint(data)
            print("----r-----")
            print(r)
            isornotexit = ElbLoadBalancers.objects.filter(load_balancer_arn=arn).exists()
            if isornotexit:
                ElbLoadBalancers.objects.filter(load_balancer_arn=arn).update(**data)
                print("----update-----")
            else:
                print("----create-----")
                ElbLoadBalancers.objects.filter(load_balancer_arn=arn).create(**data)
    ElbLoadBalancers.objects.filter(update_status=0).delete()

def aws_interface_get_elb_targe_group():
    '''
    To get the basic infomations of elb targe group by invoking the interface of the aws boto3
    :return:
    '''
    region_name_list = RegionName.objects.all().values_list("code")
    ElbTargetGroups.objects.all().update(update_status=0)
    ElbRegistryTarget.objects.all().update(update_status=0)
    for r in region_name_list:
        r = r[0]
        region_obj = RegionName.objects.get(code=r)
        client = boto3.client('elbv2', region_name=r)
        obj = client.describe_target_groups()
        elb_obj_list = obj["TargetGroups"]
        for elb_obj in elb_obj_list:
            target_arn = elb_obj["TargetGroupArn"]
            arn = elb_obj["LoadBalancerArns"]
            for single_arg in arn:
                print("-----------single_arg-----------", single_arg)
                mid_obj = ElbLoadBalancers.objects.get(load_balancer_arn=single_arg)
                data = {"load_balancer_arns":mid_obj, "attribution_area":region_obj, \
                        "port":elb_obj["Port"], "protocol":elb_obj["Protocol"], "target_group_arn":target_arn, \
                        "target_group_name":elb_obj["TargetGroupName"], "target_type":elb_obj["TargetType"], \
                        "vpc_id":elb_obj["VpcId"], "update_status":1}

                isornotexit = ElbTargetGroups.objects.filter(target_group_arn=target_arn).exists()
                if isornotexit:
                    ElbTargetGroups.objects.filter(target_group_arn=target_arn).update(**data)
                else:
                    ElbTargetGroups.objects.filter(target_group_arn=target_arn).create(**data)
                aws_interface_get_elb_registry_target(client, target_arn)
    ElbTargetGroups.objects.filter(update_status=0).delete()
    ElbRegistryTarget.objects.filter(update_status=0).delete()

def aws_interface_get_elb_registry_target(clt, arn):
    '''
    To get the basic infomations of elb registry group by invoking the interface of the aws boto3
    :param clt: the obj of boto3
    :param arn: the elb of target group arn
    :return:
    '''
    id_list =  ElbTargetGroups.objects.filter(update_status=1, target_group_arn=arn).values("id")
    target_obj = clt.describe_target_health(TargetGroupArn=arn, Targets=[])
    print("----target_obj------",target_obj)
    helth_group_obj = target_obj["TargetHealthDescriptions"]
    print(helth_group_obj)
    print(type(helth_group_obj))
    for mid_helth_group_obj in helth_group_obj:
        instance_id = mid_helth_group_obj["Target"]["Id"]
        ec2_obj = Ec2AssetInfo.objects.filter(instance_id=instance_id).values("instance_name","availability_zone")
        for ids in id_list:
            print("-------ids-------", ids,'---type----', type(ids))
            mid_elb_obj = ElbTargetGroups.objects.get(id = ids["id"])
            print("-------mid_elb_obj-------", mid_elb_obj)
            mid_keys = mid_helth_group_obj["TargetHealth"].keys()
            if "Reason" not in mid_keys:
                health_state_reason = ''
            else:
                health_state_reason = mid_helth_group_obj["TargetHealth"]["Reason"]
            if "Description" not in mid_keys:
                health_state_descript = ''
            else:
                health_state_descript = json.dumps(mid_helth_group_obj["TargetHealth"]["Description"])
            data = {"p_elb_target_group":mid_elb_obj, "instance_id":instance_id, \
                    "instance_name":ec2_obj[0]["instance_name"], "availability_zone":ec2_obj[0]["availability_zone"], \
                    "health_check_port":mid_helth_group_obj["HealthCheckPort"], \
                    "target_health_state":mid_helth_group_obj["TargetHealth"]["State"], \
                    "health_state_reason":health_state_reason, "health_state_descript":health_state_descript, "update_status":1}
            is2ornotexit = ElbRegistryTarget.objects.filter(instance_id=instance_id, p_elb_target_group__id=ids["id"]).exists()
            from pprint import pprint
            print("----data-----")
            pprint(data)
            if is2ornotexit:
                print("----------update-----------")
                ElbRegistryTarget.objects.filter(instance_id=instance_id, p_elb_target_group__id=ids["id"]).update(**data)
            else:
                print("----------create-----------")
                ElbRegistryTarget.objects.create(**data)

def aws_interface_get_rds():
    '''
    To get the basic infomations of rds invoking the interface of the aws boto3
    :return:
    '''
    region_name_list = RegionName.objects.all().values_list("code")
    RdsBasicInfo.objects.all().update(update_status=0)
    for r in region_name_list:
        r = r[0]
        region_obj = RegionName.objects.get(code=r)
        client = boto3.client('rds', region_name=r)
        obj = client.describe_db_instances()
        db_instances_list = obj["DBInstances"]
        for mid_db in db_instances_list:
            db_resource_id = mid_db["DbiResourceId"]
            data = {"db_name":mid_db["DBInstanceIdentifier"], "db_instance_status":mid_db["DBInstanceStatus"], \
                    "allocated_storage":mid_db["AllocatedStorage"], "db_instance_arn":mid_db["DBInstanceArn"], \
                    "db_instance_class":mid_db["DBInstanceClass"], "db_resource_id":db_resource_id, \
                    "engine":mid_db["Engine"], "engine_version":mid_db["EngineVersion"], \
                    "create_time":mid_db["InstanceCreateTime"], "endpoint_address":mid_db["Endpoint"]["Address"], \
                    "endpoint_port":mid_db["Endpoint"]["Port"], "attribution_area":region_obj, "update_status":1}
            from pprint import pprint
            print("-----------data-st---")
            pprint(data)
            print("-----------data----")
            is2ornotexit = RdsBasicInfo.objects.filter(db_resource_id=db_resource_id).exists()
            if is2ornotexit:
                RdsBasicInfo.objects.filter(db_resource_id=db_resource_id).update(**data)
            else:
                RdsBasicInfo.objects.create(**data)
        RdsBasicInfo.objects.filter(update_status=0).delete()

def cront_get_alb_info_interface():
    print("----st---aws_interface_get_elb_info-----")
    aws_interface_get_elb_info()
    aws_interface_get_elb_targe_group()
    print("----ed---aws_interface_get_elb_targe_group-----")
    print("----st---aws_interface_get_rds-----")
    aws_interface_get_rds()
    print("----ed---aws_interface_get_rds-----")

def zabbix_create_template_need_data_invoke(request):
    '''
    invoke the interface to get ec2 information
    :param request:
    :return: [{"instanceName":"","keyWord":"", "privateIp":""}]
    '''
    THE_SERCRET = "79be7bf0c5d506c2d58597f103f08d01"
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
       ip = request.META['REMOTE_ADDR']
    logger.info("request ip is %s"%ip)
    if request.method == 'GET':
        req_handle = request.GET
        commit_sercret = req_handle.get("sercret", "")
        if commit_sercret != THE_SERCRET:
            return JsonResponse({"result": "the sercret error"}, status=400)
        obj = Ec2AssetInfo.objects.filter(update_status=1).values("instance_key_word", \
            "instance_name", "private_ip", "availability_zone")
        ret_list = []
        for mid_obj in obj:
            ret_list.append({"instanceName":mid_obj["instance_name"], "acailabilityZone":mid_obj["availability_zone"] ,\
                             "keyWord":mid_obj["instance_key_word"], "privateIp":mid_obj["private_ip"]})
        return JsonResponse({"result": ret_list}, status=200)




def ec2_network_cpu_used_condition():
    '''
    get the condition of network/cpu by invoking the boto3 api
    :return:
    '''
    ec2_instance = Ec2AssetInfo.objects.filter(~Q(update_status=9)\
                    ).filter(instance_status="running").values("instance_id", "availability_zone")
    generator = InstanceReportGenerator()
    for mid_ec2_instance in ec2_instance:
        region_code = mid_ec2_instance["availability_zone"][:-1]
        ec2_id = mid_ec2_instance["instance_id"]
        instance_data = generator.getEC2InstancesUtil(region_code, ec2_id, 1440, 7)
        ec2_obj = Ec2AssetInfo.objects.get(instance_id=ec2_id)
        for str_date in instance_data.keys():
            cst_time = datetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
            Ec2CpuNetworkHistoryData.objects.create(ec2_instance_f = ec2_obj, \
                                    detail_day = cst_time, \
                                    cpu_utilization = instance_data[str_date]["CPUUtilization"], \
                                    network_in = instance_data[str_date]["NetworkIn"], \
                                    network_out = instance_data[str_date]["NetworkOut"])

def ec2_annotate_avg_data(st_time, ed_time):
    SERVEN_DAY_AGO = st_time
    NOW_DAY = ed_time
#    obj = Ec2CpuNetworkHistoryData.objects.filter(detail_day__range=(SERVEN_DAY_AGO, NOW_DAY)).aggregate(Avg("cpu_utilization"), Avg("network_in"), Avg("network_out"))
    obj = Ec2CpuNetworkHistoryData.objects.filter(detail_day__range=(SERVEN_DAY_AGO, NOW_DAY)).values(\
        'ec2_instance_f__instance_name', "ec2_instance_f__instance_type", "ec2_instance_f__instance_id") \
    .annotate(Avg("cpu_utilization"), Avg("network_in"), Avg("network_out"))
    return obj


@login_required
def show_Ec2_Cpu_Network_Used(request):
    '''
    show the infomations which is the Ec2 instance used condition of network/cpu
    :param request:
    :return:
    '''
    data = {}
    if request.method == "GET":
        SERVEN_DAY_AGO = GT.get_pre_later_time(-7, "%Y-%m-%d")
        NOW_DAY = GT.get_now_time("%Y-%m-%d")
        data["data"] = ec2_annotate_avg_data(SERVEN_DAY_AGO, NOW_DAY)
        data["stime"] = GT.get_pre_later_time(-7, "%d/%m/%Y")
        data["edtime"] = GT.get_pre_later_time(-1, "%d/%m/%Y")
        data["down_st_time"] = SERVEN_DAY_AGO
        data["down_ed_time"] = NOW_DAY 
        data["exit_priv"] = user_privilges_info(request)
        return render(request,'asset/show_ec2_used_condition.html',data)
    else:
        req_handle = request.POST
        get_st_time = req_handle["st_time"]
        get_ed_time = req_handle["ed_time"]
        st_time_list = get_st_time.split("/")[::-1]
        ed_time_list = get_ed_time.split("/")[::-1]
        st_time_int = int(",".join(st_time_list).replace(",",""))
        ed_time_int = int(",".join(ed_time_list).replace(",",""))
        st_time = datetime.datetime.strptime(','.join(st_time_list).replace(",","-"),"%Y-%m-%d")
        ed_time = datetime.datetime.strptime(','.join(ed_time_list).replace(",","-"),"%Y-%m-%d") + datetime.timedelta(days=1)
        if st_time_int - ed_time_int > 0:
            data["error_info"] = "<h5 style=\"color:red\">起始时间大于终止时间，请重新选择!</h5>"
        data["data"] = ec2_annotate_avg_data(st_time, ed_time)
        data["stime"] = get_st_time
        data["edtime"] = get_ed_time
        data["down_st_time"] = st_time.strftime("%Y-%m-%d")
        data["down_ed_time"] = ed_time.strftime("%Y-%m-%d")
        data["exit_priv"] = user_privilges_info(request)
        return render(request, 'asset/show_ec2_used_condition.html', data)

@login_required
def accord_time_range_down_files(request):
    if request.method == 'GET':
        st_time = request.GET["start_time"]
        print("-------st_time-------", st_time)
        ed_time = request.GET["end_time"]
        obj = ec2_annotate_avg_data(st_time, ed_time)
        file_header_list = ["instance_name", "instance_type", \
                            "CPUUtilization", "NetworkIn", "NetworkOut"]
        result_list = []
        for mid_value in obj:
            result_list.append({"instance_name":mid_value["ec2_instance_f__instance_name"],"instance_type":mid_value["ec2_instance_f__instance_type"], \
            "CPUUtilization":mid_value["cpu_utilization__avg"], "NetworkIn":mid_value["network_in__avg"], \
                     "NetworkOut":mid_value["network_out__avg"]})
        ed_time_list = ed_time.split("/")[::-1]
        file_ed_time = datetime.datetime.strptime(','.join(ed_time_list).replace(",","-"),"%Y-%m-%d") - datetime.timedelta(days=1)
        file_name = str(st_time) + "_" + str(file_ed_time.strftime("%Y-%m-%d")) +"ec2network_cpu使用情况"+ ".csv"
        print("-------file_name-------", file_name)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename='+file_name.encode('utf-8').decode('ISO-8859-1')
        writer = csv.writer(response)
        writer.writerow(file_header_list)
        for mid_data in result_list:
            writer.writerow(mid_data.values())
        return response
        #return resp
