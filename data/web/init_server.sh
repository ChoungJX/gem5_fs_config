#!/bin/bash


m5 workbegin;

sleep 1;

m5 readfile > /tmp/workload;

chmod 755 /tmp/workload;

/bin/hostname server0;

/sbin/ifconfig eth0 hw ether 00:90:00:00:00:04;

/sbin/ifconfig eth0 192.168.0.4;

/sbin/ifconfig -a;

echo "finish configuration";

echo "start to run workload";

/tmp/workload;