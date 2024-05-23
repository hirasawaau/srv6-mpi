from mininet.node import Node, Host
import re
from textwrap import wrap
from typing import List, Tuple, Any
import mininet.log as logging

DAEMONS = """
zebra=yes
ospf6d={ospf6d_enable}

vtysh_enable=yes
zebra_options=" -s 90000000 --daemon -A 127.0.0.1"
ospf6d_options=" --daemon -A ::1"
"""

VTYSH = """
hostname {name}
service integrated-vtysh-config
"""

def LoggedNode(log = True , based: type[Node] | type[Host] = Node) -> type[Node]:
    if log:
        class _Node(based):
            def cmd(self: Node | Host, *args, **kwargs):
                res = super().cmd(*args, **kwargs)
                logging.info(f'{self.name}:',*args , '\n')
                return res
        
        return _Node
    return Node

class SRv6(LoggedNode()):

    def __init__(self, name, mtu = 3000, **params):
        super().__init__(name, **params)
        self.mtu = mtu
    
    def config(self, **params):
        self.cmd('ifconfig lo up')
        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        self.cmd("sysctl -w net.ipv6.conf.all.forwarding=1")
        self.cmd("sysctl -w net.ipv6.conf.all.seg6_enabled=1")
        self.cmd("sysctl -w net.ipv6.conf.all.seg6_require_hmac=0")

        for i in self.nameToIntf.keys():
            self.cmd("sysctl -w net.ipv6.conf.{}.seg6_enabled=1".format(i))

        self.setMTUs(self.mtu)
        
    def setIPv6(self, ip: str , intf: str = None , gateway: str = None):
        return V6Host.setIPv6(self, ip , intf , gateway)
    
    def setIPv4(self, ip: str, intf: str = None, gateway: str = None):
        return V6Host.setIPv4(self, ip , intf , gateway)
    
    def setMTUs(self, mtu = 3000):
        for intf in self.nameToIntf.keys():
            self.cmd(f'ip link set dev {intf} mtu {mtu}')
    
class FRR(SRv6):
    private_dirs = ['/etc/frr' , '/var/run/frr']

    def __init__(self, name, mtu=9000, **params):
        params.setdefault('privateDirs' , [])
        params['privateDirs'].extend(self.private_dirs)
        super().__init__(name,mtu, **params)

    def set_conf(self , file: str , conf: str):
        self.cmd(f"""\
cat << 'EOF' | tee {file}
{conf}
EOF"""
        )

    def start_frr_service(self , ospf6d: bool = False):
        self.set_conf('/etc/frr/daemons', DAEMONS.format(ospf6d_enable='yes' if ospf6d else 'no'))
        self.set_conf('/etc/frr/vtysh.conf', VTYSH.format(name=self.name))
        print(self.cmd('/usr/lib/frr/frrinit.sh start'))

    
    def vtysh_cmd(self, cmd: str):
        cmds = cmd.split('\n')
        vtysh_cmd = "vtysh"
        for c in cmds:
            vtysh_cmd += " -c \"{}\"".format(c)
        return self.cmd(vtysh_cmd)
    
    def addSRv6Route(self, target: str , via: List[str], intf: str):
        self.cmd(f'ip -6 route  add {target} encap seg6 mode encap segs {",".join(via)} dev {intf}')
        # logging.info(f'ip -6 route  add {target} encap seg6 mode encap segs {",".join(via)} dev {intf}\n')

    def addStaticV4Route(self, target: str , via: str , intf: str):
        self.cmd(f'ip -4 route add {target} via {via} dev {intf}')
        # logging.info(f'ip -4 route add {target} via {via} dev {intf}\n')
    
    def addStaticV6Route(self, target: str , via: str , intf: str):
        self.cmd(f'ip -6 route add {target} via {via} dev {intf}')
        # logging.info(f'ip -6 route add {target} via {via} dev {intf}\n')
    def config(self, **params):
        super().config(**params)
        # self.start_frr_service()
    
    def tcpdump(self, subfix: str = '_dump'):
        return V6Host.tcpdump(self, subfix)
    
    
class V6Host(LoggedNode(based=Host)):

    def __init__(self, name, inNamespace=True, **params):
        super().__init__(name, inNamespace, **params)
        self.start_ssh()
        self.setMTUs()

    def setIPv6(self, ip: str , intf: str = None , gateway: str = None) -> Tuple[str | Any | None,str | Any | None]:
        intf = intf or self.defaultIntf()
        ipResult = self.cmd(f'ip -6 addr add {ip} dev {intf}')
        gwResult = None
        if gateway is not None:
            gwResult = self.cmd(f'ip -6 route add default dev {intf} via {gateway}')
        return ipResult, gwResult
    
    def setIPv4(self, ip: str, intf: str = None, gateway: str = None) -> Tuple[str | Any | None,str | Any | None]:
        intf = intf or self.defaultIntf()
        ipResult = self.cmd(f'ip -4 addr add {ip} dev {intf}')
        gwResult = None
        if gateway is not None:
            gwResult = self.cmd(f'ip -4 route add default dev {intf} via {gateway}')
        return ipResult, gwResult
    
    def start_ssh(self):
        return self.cmd('/usr/sbin/sshd -D&')
    
    def tcpdump(self, subfix: str = '_dump'):
        return self.popen(f'tcpdump -w ./dump/{self.name}{subfix}.pcap')
        
    def nginx(self):
        return self.cmd('nginx')
    
    def stop_nginx(self):
        return self.cmd('nginx -s stop')
    
    def setMTUs(self, mtu = 3000):
        for intf in self.nameToIntf.keys():
            self.cmd(f'ip link set dev {intf} mtu {mtu}')
    
    

    

class IntelV6Host(V6Host):

    def __source(self , path: str):
        self.cmd(f'source {path}')

    def config(self, *args, **kwargs):
        super().config(*args, **kwargs)
        self.__source('/opt/intel/oneapi/setvars.sh')



class IPv6Network:
    def __init__(self, networkId: str, prefix = 48) -> None:
        self.networkId = networkId
        self.prefix = prefix
    
    def getHost(self, hostId: str) -> str:
        return f'{self.networkId}::{":".join([i[::-1] for i in wrap(hostId[::-1] , 4)[::-1]])}/{self.prefix}'
    
    def createSubNetwork(self, networkId: str , prefix: int) -> 'IPv6Network':
        return IPv6Network(f'{self.networkId}:{networkId}' , prefix)
