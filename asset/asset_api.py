# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/7 15:31
# File  : asset-api.py
# Software PyCharm

import csv
from .models import  *

def scanf_asset_basic_info(**kwargs):
    try:
        return Ec2AssetInfo.objects.values("instance_name", "instance_id", "private_ip", \
               "public_ip", "instance_type", "disk_count", "disk_size", "create_time", \
               "instance_status", "availability_zone", "instance_key_word", "define_instance_tag")
    except Exception as err:
        print(err)

def write_csv_file(file_name, file_head, file_data):
    '''
    write the csv file
    :param file_name:  the file name and file path which storage file
    :param file_head: the frist row of the file .the format:["a"]
    :param file_data: the file content which formart is list: [{"a":"aaa"}]
    :return:
    '''
    with open(file_name, 'w', newline='') as csvfile:
        fieldnames = file_head
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for mid_dict in file_data:
            writer.writerow(mid_dict)
