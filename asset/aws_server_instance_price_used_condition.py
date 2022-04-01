# coding=utf8
# Autor : Dennis zhang
# Time  : 2019/1/16 17:13
# File  : ec2-report.py
# Software PyCharm


import boto3
import logging
import datetime
import time

from multiprocessing import Process, Pipe

region_dict = {
    "ap-southeast-1":"新加坡",
    "us-west-2":"俄勒冈",
    "eu-west-1":"爱尔兰",
    "ap-northeast-2":"首尔"
}
export_tags_list=[
   "prod","test","basic","ci","perf","canary","dev"
]
awsregions = {
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-1": "US West (N. California)",
    "us-west-2": "US West (Oregon)",
    "ap-south-1": "Asia Pacific (Mumbai)",
    "ap-northeast-1": "Asia Pacific (Tokyo)",
    "ap-northeast-2": "Asia Pacific (Seoul)",
    "ap-northeast-3": "Asia Pacific (Osaka-Local)",
    "ap-southeast-1": "Asia Pacific (Singapore)",
    "ap-southeast-2": "Asia Pacific (Sydney)",
    "ca-central-1": "Canada (Central)",
    "eu-west-1": "EU (Ireland)",
    "eu-west-2": "EU (London)",
    "eu-west-3": "EU (Paris)",
    "eu-north-1": "EU (Stockholm)",
    "eu-central-1" : "EU (Frankfurt)",
    "sa-east-1": "South America (Sao Paulo)"
}

ec2metrics = [
    {
        "Namespace" : "AWS/EC2",
        "MetricName" : "CPUUtilization",
        "Statistics" : ["Average"]
    },
    {
        "Namespace" : "AWS/EC2",
        "MetricName" : "NetworkIn",
        "Statistics" : ["Sum"]
    },
    {
        "Namespace" : "AWS/EC2",
        "MetricName" : "NetworkOut",
        "Statistics" : ["Sum"]
    }
]

class InstanceReportGenerator():
    def __init__(self):
        self.currentTime = datetime.datetime.utcnow()
        self.currentDate = datetime.datetime(self.currentTime.year,self.currentTime.month,self.currentTime.day)
        self.DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        self.UTIL_INTERVAL = 1440
        self.UTIL_COUNT = 30

    def enumerateAllRegionsInstances(self,  ExportTags=None):
        instanceData = []
        # Multiple threading for regions
        regionThreads = []
        regionDataFromRegionThreads = []
        for region in region_dict.keys():
            parent_conn, child_conn = Pipe()
            regionDataFromRegionThreads.append(parent_conn)

            subThread = Process(target=self.getInstancesInRegion, args=(region, child_conn, "AmazonEC2", ExportTags))
            regionThreads.append(subThread)

        for thread in regionThreads:
            thread.start()
            time.sleep(0.2)

        for thread in regionThreads:
            thread.join()

        for jsonData in regionDataFromRegionThreads:
            regionData = jsonData.recv()
            if len(regionData) > 0:
                instanceData.extend(regionData)

        return instanceData

    def getInstancesInRegion(self, region, regionsConn, serviceType='AmazonEC2', tags=None):
        print('Enumerating region %s for %s' % (region, serviceType))
        instclient = boto3.client('ec2', region_name=region)
        response = instclient.describe_instances()
        regioninstances = response['Reservations']
        instanceData = []
        instanceThreads = []
        instanceJsonFromSubThreads = []
        for reservation in regioninstances:
            for instance in reservation['Instances']:
                parent_conn, child_conn = Pipe()
                instanceJsonFromSubThreads.append(parent_conn)

                subThread = Process(target=self.getInstanceJson, args=(region, tags, instance, child_conn))
                instanceThreads.append(subThread)

        for thread in instanceThreads:
            thread.start()
            time.sleep(0.1)

        for thread in instanceThreads:
            thread.join()

        for jsonData in instanceJsonFromSubThreads:
            instanceData.append(jsonData.recv())

        regionsConn.send(instanceData)
        regionsConn.close()

    #Threading function to get the instance details
    def getInstanceJson(self, region, tags, instance, instanceConn):
        logging.info('Getting data for instance %s' % instance['InstanceId'])
        tenancy = 'Shared' if instance['Placement']['Tenancy'] == 'default' else 'Dedicated'
        spotType = instance['InstanceLifecycle'] if 'InstanceLifecycle' in instance.keys() else None
        price = self.getPriceOfInstanceType(region=region,serviceType="AmazonEC2",instanceType=instance['InstanceType'],tenancy=tenancy)
        state = instance['State']['Name']
        launchTime = instance['LaunchTime'].strftime('%Y-%m-%dT%H:%M:%sZ')
        instTags = {} if tags != None else None
        #Enumerating tags that specified
        if tags != None :
            for tag in tags:
                originalTags = instance['Tags']
                foundTags = filter(lambda singleTag: singleTag['Key'] == tag, originalTags)
                instTags[tag] = None if len(foundTags) == 0 else foundTags[0]['Value']
        utilData = self.getEC2InstancesUtil(region, instance['InstanceId'], self.UTIL_INTERVAL, self.UTIL_COUNT)
        instanceJson = {
                "Region" : region,
                "InstanceId" : instance['InstanceId'],
                "InstanceType" : instance['InstanceType'],
                "ImageId" : instance['ImageId'],
                "Tenancy" : tenancy,
                "SpotType" : spotType,
                "Price" : price,
                "State" : state,
                "LaunchTime" : launchTime,
                "UtilData" : utilData,
                "Tags" : instTags
            }
        instanceConn.send(instanceJson)
        instanceConn.close()

    #Function to get the EC2 instance utilization, the metrics included is in const.py
    def getEC2InstancesUtil(self, region, instanceId, intervalMinutes, counts):
        cwclient = boto3.client('cloudwatch', region_name=region)
        timediff = datetime.timedelta(minutes=intervalMinutes*counts)
        startTime = self.currentDate - timediff
        endTime = self.currentDate
        period = intervalMinutes * 60
        utilData = {}
        for metric in ec2metrics:
            response = cwclient.get_metric_statistics(Namespace=metric['Namespace'],\
                    MetricName=metric['MetricName'],Dimensions=[{'Name':'InstanceId','Value':instanceId}],\
                    StartTime=startTime,EndTime=endTime,Period=period,Statistics=metric['Statistics'])
            datapoints = response['Datapoints']
            print(datapoints)
            for datapoint in datapoints:

                print(datapoint)
                # roundDatetime(datapoint['Timestamp'], intervalMinutes).strftime('%Y-%m-%dT%H:%M:%sZ')
                datatimestamp = datapoint['Timestamp'].strftime(self.DATETIME_FORMAT) 
                if 'Sum' in datapoint.keys():
                    data = datapoint['Sum']
                elif 'Average' in datapoint.keys():
                    data = datapoint['Average']
                elif 'Max' in datapoint.keys():
                    data = datapoint['Max']
                elif 'Min' in datapoint.keys():
                    data = datapoint['Min']
                else:
                    data = 'N/A'
                if datatimestamp in utilData.keys():
                    utilData[datatimestamp][metric['MetricName']] = data
                else:
                    utilData[datatimestamp] = { metric['MetricName'] : data}
        #utilData = [{k : utilData[k]} for k in sorted(utilData.keys())]
        return utilData

a=InstanceReportGenerator()
a.getEC2InstancesUtil()




