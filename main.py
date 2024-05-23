from mininet.net import Mininet
from mpi_fat_tree import MpiFatTreeTopo
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from base import V6Host, FRR, IntelV6Host
from textwrap import wrap
from ipaddress import IPv6Address
import mininet.log as logging
from typing import Dict, Literal, List
import json
from subprocess import Popen
import os

IPv6_PREFIX = '2001:{ip}/{prefix}'
PREFIX='2001'


def getIPv6(network: int , host: int , prefix=64):
    hex_network = str(IPv6Address(network))[2:]
    hex_host = str(IPv6Address(host))[2:]
    return IPv6_PREFIX.format(ip=f'{hex_network}::{hex_host}', prefix=prefix)

contentFile: Dict[Literal['host', 'edge' , 'core'] , Dict[str,str | Dict[str,str]]] = {
    "host": {},
    "edge": {},
    "core": {}
}
class MPINet(Mininet):

    topo: MpiFatTreeTopo = MpiFatTreeTopo(1)
    
    def __init__(self, *args, **kwargs):
        Mininet.__init__(self, self.topo ,controller=None, *args, **kwargs)
        self.__configIPs()
        # self.__configFRR()
        self.__configStaticV4Route()
        # self.__configSRv6Route()
        self.__configStaticV6Route()

        self.__configNginx()

        
    
    def __configFRR(self):
        # Start FRR Service
        for _core in self.topo.coreRouters:
            core: FRR = self.getNodeByName(_core)
            core.start_frr_service()
        for _edge in self.topo.edgeRouters:
            edge: FRR = self.getNodeByName(_edge)
            edge.start_frr_service()
        pass

    def __configStaticV6Route(self):
        E1: FRR = self.getNodeByName('e1')
        E2: FRR = self.getNodeByName('e2')

        E1.addStaticV6Route(f'{PREFIX}:3::/64' , f'{PREFIX}:29::1' , 'e1-c1')
        E1.addStaticV6Route(f'{PREFIX}:4::/64' , f'{PREFIX}:29::1' , 'e1-c1')
        E1.addStaticV6Route(f'{PREFIX}:2a::/64', f'{PREFIX}:29::1', 'e1-c1')

        E2.addStaticV6Route(f'{PREFIX}:1::/64', f'{PREFIX}:2a::1' , 'e2-c1')
        E2.addStaticV6Route(f'{PREFIX}:2::/64', f'{PREFIX}:2a::1' , 'e2-c1')
        E2.addStaticV6Route(f'{PREFIX}:29::/64' , f'{PREFIX}:2a::1', 'e2-c1')

        C1: FRR = self.getNodeByName('c1')
        C1.addStaticV6Route(f'{PREFIX}:1::/64', f'{PREFIX}:29::2' , 'c1-e1')
        C1.addStaticV6Route(f'{PREFIX}:2::/64', f'{PREFIX}:29::2' , 'c1-e1')
        C1.addStaticV6Route(f'{PREFIX}:3::/64', f'{PREFIX}:2a::2' , 'c1-e2')
        C1.addStaticV6Route(f'{PREFIX}:4::/64', f'{PREFIX}:2a::2' , 'c1-e2')    

    
    def __configSRv6Route(self):
        # edge routing
        E1: FRR = self.getNodeByName('e1')
        E2: FRR = self.getNodeByName('e2')

        E1.addSRv6Route(f'{PREFIX}:3::/64' , [f'{PREFIX}:29::1' , f'{PREFIX}:2a::2'] , 'e1-c1')
        E1.addSRv6Route(f'{PREFIX}:4::/64' , [f'{PREFIX}:29::1' , f'{PREFIX}:2a::2'] , 'e1-c1')
        E1.addSRv6Route(f'{PREFIX}:2a::/64', [f'{PREFIX}:29::1'], 'e1-c1')

        E2.addSRv6Route(f'{PREFIX}:1::/64', [f'{PREFIX}:2a::1' , f'{PREFIX}:29::2'] , 'e2-c1')
        E2.addSRv6Route(f'{PREFIX}:2::/64', [f'{PREFIX}:2a::1' , f'{PREFIX}:29::2'] , 'e2-c1')
        E2.addSRv6Route(f'{PREFIX}:29::/64' , [f'{PREFIX}:2a::1'], 'e2-c1')

        # core routing
        # C1: FRR = self.getNodeByName('c1')
        # C1.addSRv6Route(f'{PREFIX}:1::/64', [f'{PREFIX}:29::2'] , 'c1-e1')
        # C1.addSRv6Route(f'{PREFIX}:2::/64', [f'{PREFIX}:29::2'] , 'c1-e1')
        # C1.addSRv6Route(f'{PREFIX}:3::/64', [f'{PREFIX}:2a::2'] , 'c1-e2')
        # C1.addSRv6Route(f'{PREFIX}:4::/64', [f'{PREFIX}:2a::2'] , 'c1-e2')

    def __configStaticV4Route(self):
        # edge routing
        E1: FRR = self.getNodeByName('e1')
        E2: FRR = self.getNodeByName('e2')
        C1: FRR = self.getNodeByName('c1')

        E1.addStaticV4Route('10.0.3.0/24' , '10.0.41.1' , 'e1-c1')
        E1.addStaticV4Route('10.0.4.0/24' , '10.0.41.1' , 'e1-c1')
        E2.addStaticV4Route('10.0.1.0/24' , '10.0.42.1' , 'e2-c1')
        E2.addStaticV4Route('10.0.2.0/24' , '10.0.42.1' , 'e2-c1')
        C1.addStaticV4Route('10.0.1.0/24' , '10.0.41.2' , 'c1-e1')
        C1.addStaticV4Route('10.0.2.0/24' , '10.0.41.2' , 'c1-e1')
        C1.addStaticV4Route('10.0.4.0/24' , '10.0.42.2' , 'c1-e2')
        C1.addStaticV4Route('10.0.3.0/24' , '10.0.42.2' , 'c1-e2')

    def __configIPs(self):
        # # config edge to host
        for i, hostName in enumerate(self.topo.hostNames):
            host: V6Host = self.getNodeByName(hostName)
            ip = getIPv6(i+1, 2)
            host.setIPv6(ip, 'eth0')
        
        k = 0
        for i, edgeName in enumerate(self.topo.edgeRouters):
            edge: FRR = self.getNodeByName(edgeName)
            contentFile['edge'][edgeName] = {}
            for j, hostName in enumerate(self.topo.hostNames[k:k+self.topo.h_node]):
                edgeIP = getIPv6(k+j+1, 1)
                edge.setIPv6(edgeIP, f'{edgeName}-{hostName}')
                edge.setIPv4(f'10.0.{k+j+1}.1/24' , f'{edgeName}-{hostName}')
                hostIP = getIPv6(k+j+1, 2)
                host: V6Host = self.getNodeByName(hostName)
                host.setIPv6(hostIP, 'eth0', edgeIP.split('/')[0])
                host.setIPv4(f'10.0.{k+j+1}.2/24', 'eth0', f'10.0.{k+j+1}.1')
                contentFile['host'][hostName] = hostIP
                contentFile['edge'][edgeName][f'{edgeName}-{hostName}'] = edgeIP
                logging.info(f'{edgeName} has IP: {edgeIP} interface: {edgeName}-{hostName}\n')
                logging.info(f'{hostName} has IP: {hostIP}\n')
            logging.info(self.topo.hostNames)
            k += self.topo.h_node

        # config core to edge
        BASE = 40
        for i, coreName in enumerate(self.topo.coreRouters):
            contentFile['core'][coreName] = {}
            core: FRR = self.getNodeByName(coreName)
            for j, edgeName in enumerate(self.topo.edgeRouters):
                logging.info(f'({coreName} , {edgeName})\n')
                edge: FRR = self.getNodeByName(edgeName)
                core.setIPv6(getIPv6(BASE+i+j+1, 1), f'{coreName}-{edgeName}')
                core.setIPv4(f'10.0.{BASE+i+j+1}.1/24' , f'{coreName}-{edgeName}')
                contentFile['core'][coreName][f'{coreName}-{edgeName}'] = getIPv6(BASE+i+j+1, 1)
                logging.info(f'{coreName} has IP: {getIPv6(BASE+j, 1)} interface: c{i+1}-e{j+1}\n')
                edge.setIPv6(getIPv6(BASE+i+j+1, 2), f'{edgeName}-{coreName}')
                edge.setIPv4(f'10.0.{BASE+i+j+1}.2/24' , f'{edgeName}-{coreName}')
                contentFile['edge'][edgeName][f'{edgeName}-{coreName}'] = getIPv6(BASE+i+j+1, 2)
                logging.info(f'{edgeName} has IP: {getIPv6(BASE+i+j+1, 2)} interface: e{j+1}-c{i+1}\n')

        with open('ip.json' , '+w') as f:
            json.dump(contentFile, f, ensure_ascii=False, indent=2)

    def __manuelConfigIps(self):
        pass

    def __configNginx(self):
        for _h in self.topo.hostNames:
            h: IntelV6Host = self.getNodeByName(_h)
            h.nginx()

class Dumps:

    p: List[Popen[str]]
    
    def __init__(self, *args: IntelV6Host | FRR) -> None:
        self.p = [i.tcpdump() for i in args]
    
    def terminate(self):
        for p in self.p:
            p.terminate()


def terminate_dump(*args: List[Popen[str]]):
    for p in args:
        p.terminate()

def start_dump(*args: List[IntelV6Host | FRR]) -> List[Popen[str]]:
    return [i.tcpdump() for i in args]


def main():
    setLogLevel('info')
    net = MPINet()
    h1: IntelV6Host = net.getNodeByName('h1')
    h2: IntelV6Host = net.getNodeByName('h2')
    e1: FRR = net.getNodeByName('e1')
    h3: IntelV6Host = net.getNodeByName('h3')
    e2: FRR = net.getNodeByName('e2')
    c1: FRR = net.getNodeByName('c1')
    r = Dumps(h1, e1, h3, e2, h2, c1)
    net.start()
    CLI(net)
    r.terminate()
    net.stop()

if __name__ == '__main__':
    main()
    