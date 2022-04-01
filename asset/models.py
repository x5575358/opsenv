from django.db import models

# Create your models here.

class Ec2AssetInfo(models.Model):
        id = models.AutoField(primary_key=True,help_text="id")
        instance_id=models.CharField(max_length=30,help_text="实例id")
        instance_name=models.CharField(max_length=150,help_text="实例标签名")
        define_instance_tag=models.CharField(max_length=150,help_text="费用统计实例标签名", default="")
        public_ip = models.CharField(max_length=16,help_text="公网IP",default="")
        private_ip = models.CharField(max_length=16,help_text="私网IP")
        # operator_system = models.CharField(max_length=100,help_text="操作系统")
        disk_count = models.IntegerField(help_text="硬盘数目")
        disk_size = models.IntegerField(help_text="硬盘大小")
        memory_size = models.IntegerField(help_text="内存大小")
        core_count = models.IntegerField(help_text="内核数")
        instance_key_word = models.CharField(max_length=100, help_text="实例密钥", default="")
        instance_type = models.CharField(max_length=30, help_text="实例类型", default="")
        instance_status = models.CharField(max_length=20,help_text="实例状态")
        create_time = models.DateTimeField(help_text="创建时间")
        delete_time = models.DateTimeField(auto_now=True, help_text="删除检测到的时间")
        availability_zone = models.CharField(max_length=30,help_text="可用区")
        update_status = models.IntegerField(help_text="0为更新前、1为更新完成", default="0")
        class Meta:
                permissions = (
                        ("scanf_ec2", u"查看ec2信息"),
                )

class RegionName(models.Model):
        name = models.CharField(max_length=30,help_text="地区名",default="")
        code = models.CharField(max_length=30, help_text="地区列表")

# elb负载均衡器
class ElbLoadBalancers(models.Model):
        availability_zones = models.CharField(max_length=500,help_text="可用区")
        canonical_hosted_zone_id = models.CharField(max_length=50, help_text="托管区域")
        dns_name = models.CharField(max_length=100, help_text="dns名字")
        ip_address_types = models.CharField(max_length=10, help_text="IP 地址类型")
        load_balancer_arn = models.CharField(max_length=150, help_text="ARN")
        load_balancer_name = models.CharField(max_length=50, help_text="名称")
        scheme =  models.CharField(max_length=50, help_text="模式")
        security_groups =  models.CharField(max_length=50, help_text="安全组")
        state = models.CharField(max_length=20, help_text="状态")
        types = models.CharField(max_length=35, help_text="类型")
        vpc_id = models.CharField(max_length=20, help_text="VPC")
        create_time = models.DateTimeField(help_text="创建时间")
        attribution_area = models.ForeignKey(RegionName, help_text="所属区")
        update_status = models.IntegerField(help_text="0为更新前、1为更新完成", default="1")
        class Meta:
                permissions = (
                        ("scanf_elbloadbalancers", u"查看elb负载均衡器"),
                )



# elb目标群组
class ElbTargetGroups(models.Model):
        load_balancer_arns = models.ForeignKey(ElbLoadBalancers, help_text="通过ARN来elb 负载均衡器外键")
        attribution_area = models.ForeignKey(RegionName, help_text="所属区")
        port = models.CharField(max_length=20, help_text="端口")
        protocol = models.CharField(max_length=20, help_text="协议")
        target_group_arn = models.CharField(max_length=150, help_text="目标群组ARN")
        target_group_name = models.CharField(max_length=80, help_text="目标群组名字")
        target_type = models.CharField(max_length=35, help_text="目标类型")
        vpc_id = models.CharField(max_length=20, help_text="VPC")
        update_status = models.IntegerField(help_text="0为更新前、1为更新完成", default="1")
        class  Meta:
                permissions = (
                        ("scanf_elbtargetgroups", u"查看elb目标群组"),
                )

# elb目标群组目标信息
class ElbRegistryTarget(models.Model):
        p_elb_target_group = models.ForeignKey(ElbTargetGroups, help_text="外键elb目标群组")
        instance_id = models.CharField(max_length=30, help_text="实例id")
        instance_name = models.CharField(max_length=80, help_text="实例标签名")
        availability_zone = models.CharField(max_length=30, help_text="可用区")
        health_check_port = models.CharField(max_length=20, help_text="端口")
        target_health_state = models.CharField(max_length=20, help_text="目标健康状态")
        health_state_reason = models.CharField(max_length=150, help_text="健康状态原因")
        health_state_descript = models.CharField(max_length=150, help_text="健康状态描述")
        update_status = models.IntegerField(help_text="0为更新前、1为更新完成", default="1")


# Rds基础信息
class RdsBasicInfo(models.Model):
        db_name = models.CharField(max_length=100, help_text="rds数据库名称")
        db_instance_status = models.CharField(max_length=30, help_text="数据库实例状态")
        allocated_storage = models.CharField(max_length=20, help_text="存储")
        db_instance_arn = models.CharField(max_length=150, help_text="db arn")
        db_instance_class = models.CharField(max_length=20, help_text="实例类")
        db_resource_id = models.CharField(max_length=50, help_text="实例资源id")
        engine = models.CharField(max_length=20, help_text="引擎")
        engine_version = models.CharField(max_length=20, help_text="引擎版本")
        create_time = models.DateTimeField(help_text="创建时间")
        endpoint_address = models.CharField(max_length=100, help_text="终端节点")
        endpoint_port = models.CharField(max_length=20, help_text="数据库端口")
        update_status = models.IntegerField(help_text="0为更新前、1为更新完成", default="1")
        attribution_area = models.ForeignKey(RegionName, help_text="所属区")
        class  Meta:
                permissions = (
                        ("scanf_rdsbasicinfo", u"查看rds基础信息"),
                )

class Ec2CpuNetworkHistoryData(models.Model):
        ec2_instance_f = models.ForeignKey(Ec2AssetInfo)
        detail_day = models.DateTimeField(help_text="数据时间")
        cpu_utilization = models.FloatField(help_text="cpu使用率")
        network_in = models.FloatField(help_text="入网流量")
        network_out =  models.FloatField(help_text="出网流量")
        class  Meta:
                permissions = (
                        ("scanf_ec2cpunetworkhistorydata", u"查看ec2历史使用情况"),
                )
