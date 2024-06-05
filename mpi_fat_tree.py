from mininet.topo import Topo
from mininet.link import OVSLink
from typing import List
from base import IntelV6Host
from router import SRv6

class MpiFatTreeTopo(Topo):

    coreRouters: List[str]
    edgeRouters: List[str]
    hostNames: List[str]

    def __init__(self, coreNode = 1, c_e_bw = 1000, e_t_bw = 500, h_node = 2 , *args, **params ):
        super().__init__(*args, **params)
        # 2 , 4, 8
        self.coreRouters = [self.addNode(f'c{i}' , cls=SRv6, ip=None) for i in range(1,coreNode+1)]
        self.edgeRouters = [self.addNode(f'e{i}' , cls=SRv6, ip=None) for i in range(1, len(self.coreRouters)*2 + 1)]
        self.hostNames = [self.addNode(f'h{i+1}' , cls=IntelV6Host, ip=None) for i in range(len(self.edgeRouters)*2)]
        self.h_node = h_node

        self.__build_core_edge_link(c_e_bw)
        self.__build_edge_host_link(e_t_bw)

    def __build_core_edge_link(self, bw = 1000):
        for i, core in enumerate(self.coreRouters):
            for j, edge in enumerate(self.edgeRouters):
                self.addLink(core, edge, cls=OVSLink, bw=bw, delay='1ms',
                            intfName1=f'c{i+1}-e{j+1}', intfName2=f'e{j+1}-c{i+1}'    
                             )

    def __build_edge_host_link(self, bw = 500):
        k = 0
        for i, edge in enumerate(self.edgeRouters):
            for j, host in enumerate(self.hostNames[k:k+self.h_node]):
                self.addLink(edge, host, cls=OVSLink, bw=bw, delay='1ms',
                             intfName1=f'e{i+1}-h{k+j+1}', intfName2=f'eth0'
                             )
            k += self.h_node



    