#!/bin/bash

#m5 checkpoint 1
#sleep 2

# m5 workbegin
# #sleep 1
# m5 readfile > /tmp/workload
# chmod 755 /tmp/workload

# m5 workbegin
# #sleep 1
# m5 readfile > /tmp/run.sh
# chmod 755 /tmp/run.sh
# /tmp/run.sh
# cat "boot success"
# service postgresql start

/bin/hostname database
/sbin/ifconfig eth0 hw ether 00:90:00:00:00:05
/sbin/ifconfig eth0 192.168.0.5 netmask 255.255.255.0 up
/sbin/ifconfig -a

sleep 1
sudo ip link set lo up

mongod --bind_ip 192.168.0.5 --noauth
# service postgresql start
# pg_ctlcluster 10 main start
# su - postgres
# /usr/lib/postgresql/9.6/bin/pg_ctl -D /var/lib/postgresql/9.6/main -l logfile start