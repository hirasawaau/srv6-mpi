from mininet.net import Mininet
from mpi_fat_tree import MpiFatTreeTopo
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from base import V6Host, FRR
from textwrap import wrap
from ipaddress import IPv6Address
import mininet.log as logging

IPv6_PREFIX = 'fd00:2a35:1d48:{ip}/{prefix}'


def getIPv6(network: int , host: int , prefix= 64):
    if(network > 2**16 or host > 2**64):
        raise ValueError('Invalid IPv6 address')
    hex_network = str(IPv6Address(network))[2:]
    hex_host = str(IPv6Address(host))[2:]
    return IPv6_PREFIX.format(ip=f'{hex_network}::{hex_host}', prefix=prefix)


class MPINet(Mininet):

    topo: MpiFatTreeTopo = MpiFatTreeTopo()
    
    def __init__(self, *args, **kwargs):
        Mininet.__init__(self, self.topo ,controller=None, *args, **kwargs)
        self.__configIPs()

    def __configIPs(self):
        # config edge to host
        for i, hostName in enumerate(self.topo.hostNames):
            host: V6Host = self.getNodeByName(hostName)
            ip = getIPv6(i+1, 2)
            host.setIPv6(ip, 'eth0')
            logging.info(f'{hostName} has IP: {ip}\n')
        
        k = 0
        for i, edgeName in enumerate(self.topo.edgeRouters):
            edge: FRR = self.getNodeByName(edgeName)
            for j, hostName in enumerate(self.topo.hostNames[k:k+5]):
                edge.setIPv6(getIPv6(k+j+1, 1), f'e{i+1}-h{j+1}')
                logging.info(f'{edgeName} has IP: {getIPv6(k+j+1, 1)} interface: e{i+1}-h{j+1}\n')
            k += 5

        # config core to edge
        BASE = 40
        for i, coreName in enumerate(self.topo.coreRouters):
            core: FRR = self.getNodeByName(coreName)
            for j, edgeName in enumerate(self.topo.edgeRouters):
                edge: FRR = self.getNodeByName(edgeName)
                core.setIPv6(getIPv6(BASE+i+j+1, 1), f'c{i+1}-e{j+1}')
                logging.info(f'{coreName} has IP: {getIPv6(BASE+j, 1)} interface: c{i+1}-e{j+1}\n')
                edge.setIPv6(getIPv6(BASE+i+j+1, 2), f'e{j+1}-c{i+1}')
                logging.info(f'{edgeName} has IP: {getIPv6(BASE+i+j+1, 2)} interface: e{j+1}-c{i+1}\n')
            

            




def main():
    setLogLevel('info')
    net = MPINet()
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()