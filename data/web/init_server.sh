#!/bin/bash

# m5 checkpoint 1
# sleep 2

# export ACTIX_TECHEMPOWER_MONGODB_URL="mongodb://192.168.0.5:27017"
m5 workbegin
sleep 1
m5 readfile > /tmp/workload
chmod 755 /tmp/workload

/bin/hostname server0
/sbin/ifconfig eth0 hw ether 00:90:00:00:00:04
/sbin/ifconfig eth0 192.168.0.4
/sbin/ifconfig -a
echo "finish"

/tmp/workload