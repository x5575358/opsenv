import boto3

from .models import Ec2AssetInfo
from django.db.models import Q

def auto_create_tag():
    obj = Ec2AssetInfo.objects.filter(availability_zone__startswith="ap-southeast-1").filter(~Q(update_status=9)).values("instance_id","availability_zone")
    ec2 = boto3.resource('ec2', region_name="ap-southeast-1")
    tag_list = ["UsageService","APP-ApiGateway","APP-Backend","APP-Config","APP-Download","APP-ES","PP-H5Openapi","PP-H5Reg","EMR","OPS","OPS-CICDTools","OPS-CMDB","OPS-Code","OPS-CodeStaticAnalysis","OPS-DockerImageReg","OPS-ETL","OPS-JARTools","OPS-Jump","OPS-Jump&SS","OPS-Log","OPS-Monitor","OPS-OpenLDAP","OPS-SS","Report","RISK","VPN","WP-OfficalWebSite","UsageCountry","UsageOs"]
    tag_values_list = []
    for tag in tag_list:
        tag_values_list.append({'Key':tag,'Value':''})
    for i in obj:
        r = i["availability_zone"][:-1]
        ids = i["instance_id"]
        instance_h = ec2.Instance(ids)
        p = instance_h.create_tags(Tags=tag_values_list)
  #          print("----p===",p)
    print("----over----auto_create_tag----888---")

def auto_delete_tag():
    obj = Ec2AssetInfo.objects.filter(availability_zone__startswith="us-east-2").filter(~Q(update_status=9)).values("instance_id","availability_zone")
    ec2 = boto3.resource('ec2', region_name="us-east-2")
    tag_list = ["APP-ApiGateway","APP-Backend","APP-Config","APP-Download","APP-ES","PP-H5Openapi","PP-H5Reg","EMR","OPS","OPS-CICDTools","OPS-CMDB","OPS-Code","OPS-CodeStaticAnalysis","OPS-DockerImageReg","OPS-ETL","OPS-JARTools","OPS-Jump","OPS-Jump&SS","OPS-Log","OPS-Monitor","OPS-OpenLDAP","OPS-SS","Report","RISK","VPN","WP-OfficalWebSite"]
    tag_values_list = []
    for tag in tag_list:
        tag_values_list.append({'Key':tag,'Value':''})
    for i in obj:
        ids = i["instance_id"]
        instance_h = ec2.Instance(ids)
        p = instance_h.delete_tags(Tags=tag_values_list)
