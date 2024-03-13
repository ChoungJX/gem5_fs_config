
/bin/hostname server0
/sbin/ifconfig eth0 hw ether 00:90:00:00:00:04
/sbin/ifconfig eth0 192.168.0.4
/sbin/ifconfig -a
echo "finish"
sleep 1000
m5 workbegin;/tmp/workload
