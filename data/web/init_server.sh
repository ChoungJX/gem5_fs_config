#!/bin/bash

service haveged start
# haveged -b 512
m5 workbegin

echo "load workload binary"
m5 readfile > /tmp/workload
chmod 755 /tmp/workload

echo "set server ip"
/bin/hostname server0
/sbin/ifconfig eth0 hw ether 00:90:00:00:00:04
/sbin/ifconfig eth0 192.168.0.4
/sbin/ifconfig -a

echo "ping client test"
ping 192.168.0.6 -c 3

m5 workbegin
echo "load database file"
m5 readfile > /root/hello_world.db

echo "finish configuration"

echo "start to run workload"

DATABASE_URL=/root/hello_world.db /tmp/workload