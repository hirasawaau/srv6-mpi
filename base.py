from mininet.node import Node, Host
import re
from textwrap import wrap

DAEMONS = """
zebra=yes
ospf6d=yes

vtysh_enable=yes
zebra_options=" -s 90000000 --daemon -A 127.0.0.1"
ospf6d_options=" --daemon -A ::1"
"""

VTYSH = """
hostname {name}
service integrated-vtysh-config
"""

class SRv6(Node):

    def __init__(self, name, **params):
        super().__init__(name, **params)
    
    def config(self, **params):
        self.cmd('ifconfig lo up')
        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        self.cmd("sysctl -w net.ipv6.conf.all.forwarding=1")
        self.cmd("sysctl -w net.ipv6.conf.all.seg6_enabled=1")
        self.cmd("sysctl -w net.ipv6.conf.all.seg6_require_hmac=0")

        for i in self.nameToIntf.keys():
            self.cmd("sysctl -w net.ipv6.conf.{}.seg6_enabled=1".format(i))
        
    def setIPv6(self, ip: str , intf: str = None , gateway: str = None):
        intf = intf or self.defaultIntf()
        if gateway:
            self.cmd(f'ip -6 route add default via {gateway} dev {intf}')
        return self.cmd(f'ip -6 addr add {ip} dev {intf}')
    
class FRR(SRv6):
    private_dirs = ['/etc/frr' , '/var/run/frr']

    def __init__(self, name, **params):
        params.setdefault('privateDirs' , [])
        params['privateDirs'].extend(self.private_dirs)
        super().__init__(name, **params)

    def set_conf(self , file: str , conf: str):
        self.cmd(f"""\
cat << 'EOF' | tee {file}
{conf}
EOF"""
        )

    def start_frr_service(self):
        self.set_conf('/etc/frr/daemons', DAEMONS)
        self.set_conf('/etc/frr/vtysh.conf', VTYSH.format(name=self.name))
        print(self.cmd('/usr/lib/frr/frrinit.sh start'))
    
    def vtysh_cmd(self, cmd: str):
        cmds = cmd.split('\n')
        vtysh_cmd = "vtysh"
        for c in cmds:
            vtysh_cmd += " -c \"{}\"".format(c)
        return self.cmd(vtysh_cmd)
    
    
class V6Host(Host):

    def __init__(self, name, inNamespace=True, **params):
        super().__init__(name, inNamespace, **params)

    def setIPv6(self, ip: str , intf: str = None , gateway: str = None):
        intf = intf or self.defaultIntf()
        if gateway:
            self.cmd(f'ip -6 route add default via {gateway} dev {intf}')
        return self.cmd(f'ip -6 addr add {ip} dev {intf}')



class IPv6Network:
    def __init__(self, networkId: str, prefix = 48) -> None:
        self.networkId = networkId
        self.prefix = prefix
    
    def getHost(self, hostId: str) -> str:
        return f'{self.networkId}::{":".join([i[::-1] for i in wrap(hostId[::-1] , 4)[::-1]])}/{self.prefix}'
    
    def createSubNetwork(self, networkId: str , prefix: int) -> 'IPv6Network':
        return IPv6Network(f'{self.networkId}:{networkId}' , prefix)
