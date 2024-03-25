
sleep 1

m5 workbegin

sleep 1

m5 readfile > /tmp/workload

chmod 755 /tmp/workload

/bin/hostname client

/sbin/ifconfig eth0 hw ether 00:90:00:00:00:06
/sbin/ifconfig eth0 192.168.0.6 netmask 255.255.255.0 up

/sbin/ifconfig -a


sleep 3

curl http://192.168.0.4:3000

echo "finished curl test"

sleep 1

echo "start to run wrk"

/tmp/workload -t8 -c800 -d5s http://192.168.0.4:3000