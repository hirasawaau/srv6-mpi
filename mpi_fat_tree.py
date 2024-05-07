from mininet.topo import Topo
from mininet.link import OVSLink
from typing import List
from base import FRR, SRv6, V6Host

class MpiFatTreeTopo(Topo):

    coreRouters: List[str]
    edgeRouters: List[str]
    hostNames: List[str]

    def __init__(self, *args, **params):
        super().__init__(*args, **params)
        self.coreRouters = [self.addNode(f'c{i}' , cls=FRR, ip=None) for i in range(1,5)]
        self.edgeRouters = [self.addNode(f'e{i}' , cls=FRR, ip=None) for i in range(1, len(self.coreRouters)*2 + 1)]
        self.hostNames = [self.addNode(f'h{i+1}' , cls=V6Host, ip=None) for i in range(len(self.edgeRouters)*5)]

        self.__build_core_edge_link()
        self.__build_edge_host_link()

    def __build_core_edge_link(self):
        for i, core in enumerate(self.coreRouters):
            for j, edge in enumerate(self.edgeRouters):
                self.addLink(core, edge, cls=OVSLink, bw=1000, delay='1ms',
                            intfName1=f'c{i+1}-e{j+1}', intfName2=f'e{j+1}-c{i+1}'    
                             )

    def __build_edge_host_link(self):
        k = 0
        for i, edge in enumerate(self.edgeRouters):
            for j, host in enumerate(self.hostNames[k:k+5]):
                self.addLink(edge, host, cls=OVSLink, bw=100, delay='1ms',
                             intfName1=f'e{i+1}-h{k+j+1}', intfName2=f'eth0'
                             )
            k += 5
    

    