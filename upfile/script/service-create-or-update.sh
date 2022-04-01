#!/bin/bash

Image=$1

FullserviceName=$(echo $Image | awk -F/ {'print $3'})
serviceName=$(echo $FullserviceName | awk -F: {'print $1'})

serviceCount=$(docker ps|grep $serviceName:|wc -l)
if [ $serviceCount != 0 ]; then
	docker pull $Image
	docker service update $serviceName --update-delay 10s --image $Image
else
	serviceTag=$(echo $fullserviceName | awk -F: {'print $2'})

	docker login -p xxxxxx -u ciadmin reg.xxxxxx.net
	docker pull $Image
	#consulHost="ip:8500"
	configcenter="http://ip:11111"
	envlabel="master"


	#set JVM_HEAPS
	mem='1280m'
	#get service HOSTIP
	serverHOSTIP=$(/sbin/ifconfig eth0 | grep -w inet | awk {'print $2'})
	#ServerPort=$2

	case $serviceName in
	  "account" )
		ServerPort=18080
		;;
	  "account-service" )
		ServerPort=18081
		;;
	  "basic-data" )
		ServerPort=18180
		;;
	  "c-front" )
		ServerPort=18082
		;;
	  "device" )
		ServerPort=18181
		;;
	  "flutterwave" )
		ServerPort=18083
		;;
	  "loyalty" )
		ServerPort=18084
		;;
	  "m-aa" )
		ServerPort=18085
		;;
	  "member" )
		ServerPort=18086
		;;
	  "m-front" )
		ServerPort=18087
		;;
	  "pay-route" )
		ServerPort=18088
		;;
	  "push" )
		ServerPort=18182
	   ;;
	  "risk-control" )
		ServerPort=18183
		;;
	  "sms" )
		ServerPort=18184
		;;
	  "validator" )
		ServerPort=18185
		;;
	  "product-service" )
		ServerPort=18089
		;;
	  "trade" )
		ServerPort=18090
		;;
	  "cash-in-out" )
		ServerPort=18091
		;;
	  "send-money" )
		ServerPort=18092
		;;
	  "airtime" )
		ServerPort=18093
		;;
	  "bill" )
		ServerPort=18094
		;;
	  "query" )
		ServerPort=18186
		;;
	  "message" )
		ServerPort=18187
		;;
	  "m-workflow" )
		ServerPort=18188
		;;
	  "m-customer-management" )
		ServerPort=18189
		;;
	  "collect" )
		ServerPort=18190
		;;
	  "paystack" )
		ServerPort=18095
		;;
	  "rave" )
		ServerPort=18096
		;;
	  "marketing" )
		ServerPort=18097
		;;
	  "mail" )
		ServerPort=18191
		;;
	  "settlement" )
		ServerPort=18098
		;;
	  "quickteller" )
		ServerPort=18099
		;;
	 "selcom" )
		ServerPort=18193
		;;
	 "loan" )
		ServerPort=18192
		;;
	 "merchant" )
		ServerPort=18194
		;;
	  "" )
	   echo "You MUST offer serviceName,ex> {$0 re-run with serviceName}"
		;;
	esac

	echo "$serviceName will deploy on $serverHOSTIP:$ServerPort..."

	docker service create --name=$serviceName --limit-memory $mem -e LABEL=$envlabel -e CONFIGURL=$configcenter -e SPORT=$ServerPort -e HOSTIP=$serverHOSTIP --mount type=bind,source=/data/applogs,dst=/logs --mode global --publish mode=host,target=$ServerPort,published=$ServerPort $Image
fi
