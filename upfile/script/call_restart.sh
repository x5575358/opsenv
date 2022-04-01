#!/bin/bash
rm -rf /home/ec2-user/upfile/opsserver/nohup.out
file_name=$1
file_path=$2
echo  $file_path>>/home/ec2-user/upfile/opsserver/a.txt
echo  $file_name>>/home/ec2-user/upfile/opsserver/b.txt
nohup /home/ec2-user/upfile/opsserver/restart_clean_container.sh $file_path $file_name &
