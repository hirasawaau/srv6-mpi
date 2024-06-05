from mininet.topo import Topo
from base import V6Host
from router import FRR, SRv6
from mininet.link import OVSLink
from typing import Self, Literal

router_configs = {
    "c1": """
enable
configure terminal
interface c1-e1
ip address 172.16.177.1/24
exit

interface c1-e2
ip address 172.16.178.1/24
exit

interface c1-e3
ip address 172.16.179.1/24
exit

interface c1-e4
ip address 172.16.180.1/24
exit

router ospf
ospf router-id 0.0.0.1
redistribute connected
network 172.16.177.0/24 area 0
network 172.16.178.0/24 area 0
network 172.16.179.0/24 area 0
network 172.16.180.0/24 area 0
exit
""",
    "c2": """
enable
configure terminal
interface c2-e1
ip address 172.16.193.1/24
exit

interface c2-e2
ip address 172.16.194.1/24
exit

interface c2-e3
ip address 172.16.195.1/24
exit

interface c2-e4
ip address 172.16.196.1/24
exit

router ospf
ospf router-id 0.0.0.2
redistribute connected
network 172.16.193.0/24 area 0
network 172.16.194.0/24 area 0
network 172.16.195.0/24 area 0
network 172.16.196.0/24 area 0
exit
""",
    "e1":"""
enable
configure terminal
interface e1-c1
ip address 172.16.177.2/24
exit

interface e1-c2
ip address 172.16.193.2/24
exit

interface e1-h1
ip address 172.16.1.1/24
exit

interface e1-h2
ip address 172.16.2.1/24
exit

router ospf
ospf router-id 0.0.1.1
redistribute connected
network 172.16.177.0/24 area 0
network 172.16.193.0/24 area 0
network 172.16.1.0/24 area 0
network 172.16.2.0/24 area 0
exit
""",
    "e2":"""
enable
configure terminal
interface e2-c1
ip address 172.16.178.2/24
exit

interface e2-c2
ip address 172.16.194.2/24
exit

interface e2-h3
ip address 172.16.3.1/24
exit

interface e2-h4
ip address 172.16.4.1/24
exit

router ospf
ospf router-id 0.0.1.2
redistribute connected
network 172.16.178.0/24 area 0
network 172.16.194.0/24 area 0
network 172.16.3.0/24 area 0
network 172.16.4.0/24 area 0
exit
""",
    "e3":"""
enable
configure terminal
interface e3-c1
ip address 172.16.179.2/24
exit

interface e3-c2
ip address 172.16.195.2/24
exit

interface e3-h5
ip address 172.16.5.1/24
exit

interface e3-h6
ip address 172.16.6.1/24
exit

router ospf
ospf router-id 0.0.1.3
redistribute connected
network 172.16.177.0/24 area 0
network 172.16.193.0/24 area 0
network 172.16.1.0/24 area 0
network 172.16.2.0/24 area 0
exit
""",
    "e4":"""
enable
configure terminal
interface e4-c1
ip address 172.16.180.2/24
exit

interface e4-c2
ip address 172.16.196.2/24
exit

interface e4-h7
ip address 172.16.7.1/24
exit

interface e4-h8
ip address 172.16.8.1/24
exit

router ospf
ospf router-id 0.0.1.4
redistribute connected
network 172.16.188.0/24 area 0
network 172.16.196.0/24 area 0
network 172.16.7.0/24 area 0
network 172.16.8.0/24 area 0
exit
"""
}

router_configs_v6 = {
    
}

class BigFatTreeTopo(Topo):
    h_node = 2
    def __init__(self,c_e_bw = 100 , e_t_bw = 50, *args, **params ):
        super().__init__(*args, **params)


        self.coreRouters = [self.addNode(f'c1', cls=SRv6, ip=None) , self.addNode(f'c2' , cls=SRv6 , ip=None)]
        # 2 , 4, 8
        self.edgeRouters = [self.addNode(f'e{i}' , cls=SRv6, ip=None) for i in range(1, 5)]
        self.hostNames = [self.addNode(f'h{i+1}' , cls=V6Host, ip=None) for i in range(8)]

        self.__build_core_edge_link(c_e_bw)
        self.__build_edge_host_link(e_t_bw)

    def __build_core_edge_link(self, bw = 1000):
        for j, c in enumerate(self.coreRouters):
            for i,e in enumerate(self.edgeRouters):
                self.addLink(c, e, cls=OVSLink, bw=bw,
                            intfName1=f'c{j+1}-e{i+1}', intfName2=f'e{i+1}-c{j+1}'
                            )

    def __build_edge_host_link(self, bw = 500):
        k = 0
        for i, edge in enumerate(self.edgeRouters):
            for j, host in enumerate(self.hostNames[k:k+self.h_node]):
                self.addLink(edge, host, cls=OVSLink, bw=bw, delay='1ms',
                             intfName1=f'e{i+1}-h{k+j+1}', intfName2=f'eth0'
                             )
            k += self.h_node

class BigFatTreeTopoV4(Topo):
    h_node = 2
    def __init__(self,c_e_bw = 100 , e_t_bw = 50, *args, **params ):
        super().__init__(*args, **params)


        self.coreRouters = [self.addNode(f'c1', cls=FRR, ip=None, router_config=router_configs[f'c1']) , self.addNode(f'c2' , cls=FRR , ip=None, router_configs=router_configs[f'c2'])]
        # 2 , 4, 8
        self.edgeRouters = [self.addNode(f'e{i}' , cls=FRR, ip=None , router_config=router_configs[f'e{i}']) for i in range(1, 5)]
        self.hostNames = [self.addNode(f'h{i+1}' , cls=V6Host, ip=None) for i in range(8)]

        self.__build_core_edge_link(c_e_bw)
        self.__build_edge_host_link(e_t_bw)

    def __build_core_edge_link(self, bw = 1000):
        for j, c in enumerate(self.coreRouters):
            for i,e in enumerate(self.edgeRouters):
                self.addLink(c, e, cls=OVSLink, bw=bw,
                            intfName1=f'c{j+1}-e{i+1}', intfName2=f'e{i+1}-c{j+1}'
                            )

    def __build_edge_host_link(self, bw = 500):
        k = 0
        for i, edge in enumerate(self.edgeRouters):
            for j, host in enumerate(self.hostNames[k:k+self.h_node]):
                self.addLink(edge, host, cls=OVSLink, bw=bw, delay='1ms',
                             intfName1=f'e{i+1}-h{k+j+1}', intfName2=f'eth0'
                             )
            k += self.h_node

    
