from mininet.node import Node, Host
import re
from textwrap import wrap
from typing import List, Tuple, Any
import mininet.log as logging
from typing import Dict
from subprocess import Popen

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
                logging.info(f'{self.name}:', res , '\n\n')
                return res
            
            def popen(self, *args, **kwargs) -> Popen[str]:
                res = super().popen(*args, **kwargs)
                logging.info(f'{self.name}:',*args , '\n')
                logging.info(f'{self.name}:', res , '\n\n')
                return res       
        return _Node
    return based


    
    

    
class V6Host(LoggedNode(based=Host)):

    ip: Dict[str , str] = {}

    def __init__(self, name, inNamespace=True, **params):
        super().__init__(name, inNamespace, **params)
        self.start_ssh()
        self.setMTUs(9000)

    def setIPv6(self, ip: str , intf: str = None , gateway: str = None) -> Tuple[str | Any | None,str | Any | None]:
        intf = intf or self.defaultIntf()
        ipResult = self.cmd(f'ip -6 addr add {ip} dev {intf}')
        gwResult = None
        if gateway is not None:
            gwResult = self.cmd(f'ip -6 route add default dev {intf} via {gateway}')
        self.ip[intf] = ip
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
        self.cmd(f'ip link set dev eth0 mtu {mtu}')
        
    

    

class IntelV6Host(V6Host):

    def __source(self , path: str):
        self.cmd(f'source {path}')

    def config(self, *args, **kwargs):
        super().config(*args, **kwargs)
        self.__source('/opt/intel/oneapi/setvars.sh')

    def __init__(self, name, inNamespace=True, **params):
        super().__init__(name, inNamespace, **params)



class IPv6Network:
    def __init__(self, networkId: str, prefix = 48) -> None:
        self.networkId = networkId
        self.prefix = prefix
    
    def getHost(self, hostId: str) -> str:
        return f'{self.networkId}::{":".join([i[::-1] for i in wrap(hostId[::-1] , 4)[::-1]])}/{self.prefix}'
    
    def createSubNetwork(self, networkId: str , prefix: int) -> 'IPv6Network':
        return IPv6Network(f'{self.networkId}:{networkId}' , prefix)
