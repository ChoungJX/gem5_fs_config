with open("s_server.sh","w") as wFile:
    wFile.write("""
/bin/hostname server0
/sbin/ifconfig eth0 hw ether 00:90:00:00:00:04
/sbin/ifconfig eth0 192.168.0.4
/sbin/ifconfig -a
m5 workbegin;/tmp/workload
""")
    

import uuid
import random
import string

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

for i in range(20):
    uuid_pools = {}
    with open("s_client_%s.sh"%(i+1),"w") as wFile:
        wFile.write(f"/bin/hostname client{i+1}\n")
        wFile.write(f"/sbin/ifconfig eth0 hw ether 00:90:00:00:00:{'0' + str(i + 5) if i + 5 < 10 else i + 5}\n")
        wFile.write(f"/sbin/ifconfig eth0 192.168.0.{i + 5} netmask 255.255.255.0 up\n")
        wFile.write(f"/sbin/ifconfig -a\n")
        wFile.write(f"sleep 3\n")
        # wFile.write(f"ping -c 3 192.168.0.4;sleep 3;\n")
        

        for j in range(10):
            g_key = generate_random_string(32)
            g_value = generate_random_string(32)
            uuid_pools[g_key] = g_value
            wFile.write(f"/tmp/workload --hostname 192.168.0.4 set {g_key} {g_value}\n")
        
        for j in range(10):
            g_key = generate_random_string(32)
            g_value = generate_random_string(640)
            uuid_pools[g_key] = g_value
            wFile.write(f"/tmp/workload --hostname 192.168.0.4 set {g_key} {g_value}\n")

        for j in range(100):
            pick_list = list(uuid_pools.keys())
            wFile.write(f"/tmp/workload --hostname 192.168.0.4 get {random.choice(pick_list)}\n")
        
        wFile.write(f"m5 workend\n")
        wFile.write(f"m5 exit\n")