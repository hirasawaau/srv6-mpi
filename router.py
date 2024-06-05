from base import LoggedNode, V6Host
from typing import Dict, List

class Router(LoggedNode()):
    ip: Dict[str , str] = {}

    def __init__(self, name, mtu = 9000, **params):
        super().__init__(name, **params)
        self.mtu = mtu
    
    def config(self, **params):
        self.cmd('ifconfig lo up')
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

        self.setMTUs(self.mtu)
    
    def setIPv6(self, ip: str , intf: str = None , gateway: str = None):
        return V6Host.setIPv6(self, ip , intf , gateway)
    
    def setIPv4(self, ip: str, intf: str = None, gateway: str = None):
        return V6Host.setIPv4(self, ip , intf , gateway)

    def setMTUs(self, mtu = 3000):
        for intf in self.nameToIntf.keys():
            self.cmd(f'ip link set dev {intf} mtu {mtu}')
    def tcpdump(self, subfix: str = '_dump'):
        return V6Host.tcpdump(self, subfix)
 


    

class SRv6(Router):
        
    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv6.conf.all.forwarding=1")
        self.cmd("sysctl -w net.ipv6.conf.all.seg6_enabled=1")
        self.cmd("sysctl -w net.ipv6.conf.all.seg6_require_hmac=0")

        for i in self.nameToIntf.keys():
            self.cmd("sysctl -w net.ipv6.conf.{}.seg6_enabled=1".format(i))
    
    
    def addSRv6Route(self, target: str , via: List[str], intf: str):
        self.cmd(f'ip -6 route  add {target} encap seg6 mode encap segs {",".join(via)} dev {intf}')
        # logging.info(f'ip -6 route  add {target} encap seg6 mode encap segs {",".join(via)} dev {intf}\n')

    def addStaticV4Route(self, target: str , via: str , intf: str):
        self.cmd(f'ip -4 route add {target} via {via} dev {intf}')
        # logging.info(f'ip -4 route add {target} via {via} dev {intf}\n')
    
    def addStaticV6Route(self, target: str , via: str , intf: str):
        self.cmd(f'ip -6 route add {target} via {via} dev {intf}')
        # logging.info(f'ip -6 route add {target} via {via} dev {intf}\n')
        # self.start_frr_service()
    
    
  
    
class FRR(Router):
    private_dirs = ['/etc/frr' , '/var/run/frr']
    
    CONFIG: str
    def __init__(self, name, mtu=9000, **params):
        params.setdefault('privateDirs' , [])
        params['privateDirs'].extend(self.private_dirs)
        super().__init__(name,mtu, **params)
        self.DAEMONS=f"""
ospfd=yes
vtysh_enable=yes
"""
        self.VTYSH=f"""
hostname {name}
service integrated-vtysh-config
"""
    def set_conf(self , file: str , conf: str):
        self.cmd(f"""\
cat << 'EOF' | tee {file}
{conf}
EOF"""
        )
    def start_frr_service(self , ospf6d: bool = False):
        self.set_conf('/etc/frr/daemons', self.DAEMONS)
        self.set_conf('/etc/frr/vtysh.conf', self.VTYSH)
        self.cmd('/usr/lib/frr/frrinit.sh start')
    
    def vtysh_cmd(self, cmd: str):
        cmds = cmd.split('\n')
        vtysh_cmd = "vtysh"
        for c in cmds:
            vtysh_cmd += " -c \"{}\"".format(c)
        return self.cmd(vtysh_cmd)
    
    def config(self, **params):
        super().config(**params)
        self.start_frr_service()




RouterType = FRR | SRv6
