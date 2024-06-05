from big_fat_tree_topo import BigFatTreeTopo, BigFatTreeTopoV4, router_configs
from mininet.net import Mininet
from base import V6Host
from mininet.cli import CLI
from mininet.log import setLogLevel
from _main import Dumps
from typing import Self, Literal
from router import FRR, SRv6, RouterType


class Net(Mininet):
    c1: RouterType
    c2: RouterType
    e1: RouterType
    e2: RouterType
    e3: RouterType
    e4: RouterType
    h1: V6Host
    h2: V6Host
    h3: V6Host
    h4: V6Host
    h5: V6Host
    h6: V6Host
    h7: V6Host
    h8: V6Host


    def __init__(self,v:Literal['v4','v6'] = 'v6', *args, **kwargs):
        self.topo = BigFatTreeTopoV4() if v == 'v4' else BigFatTreeTopo()
        super().__init__(topo=self.topo,controller=None,*args, **kwargs)
        self.setMTUs(9000)
    

    def setMTUs(self, mtu: int):
        self.c1.setMTUs(mtu)
        self.c2.setMTUs(mtu)
        self.e1.setMTUs(mtu)
        self.e2.setMTUs(mtu)
        self.e3.setMTUs(mtu)
        self.e4.setMTUs(mtu)
        self.h1.setMTUs(mtu)
        self.h2.setMTUs(mtu)
        self.h3.setMTUs(mtu)
        self.h4.setMTUs(mtu)
        self.h5.setMTUs(mtu)
        self.h6.setMTUs(mtu)
        self.h7.setMTUs(mtu)
        self.h8.setMTUs(mtu)

    def configIPv6s(self):
        

        # IPv6
        # Core
        self.c1.setIPv6('2001:b1::1/64' , 'c1-e1')
        self.c1.setIPv6('2001:b2::1/64' , 'c1-e2')
        self.c1.setIPv6('2001:b3::1/64' , 'c1-e3')
        self.c1.setIPv6('2001:b4::1/64' , 'c1-e4')
        self.c2.setIPv6('2001:c1::1/64' , 'c2-e1')
        self.c2.setIPv6('2001:c2::1/64' , 'c2-e2')
        self.c2.setIPv6('2001:c3::1/64' , 'c2-e3')
        self.c2.setIPv6('2001:c4::1/64' , 'c2-e4')


        # Edge

        # Edge to Core
        self.e1.setIPv6('2001:b1::2/64' , 'e1-c1')
        self.e2.setIPv6('2001:b2::2/64' , 'e2-c1')
        self.e3.setIPv6('2001:b3::2/64' , 'e3-c1')
        self.e4.setIPv6('2001:b4::2/64' , 'e4-c1')

        self.e1.setIPv6('2001:c1::2/64' , 'e1-c2')
        self.e2.setIPv6('2001:c2::2/64' , 'e2-c2')
        self.e3.setIPv6('2001:c3::2/64' , 'e3-c2')
        self.e4.setIPv6('2001:c4::2/64' , 'e4-c2')

        # Edge to Host
        self.e1.setIPv6('2001:1::1/64' , 'e1-h1')
        self.e1.setIPv6('2001:2::1/64' , 'e1-h2')
        self.e2.setIPv6('2001:3::1/64' , 'e2-h3')
        self.e2.setIPv6('2001:4::1/64' , 'e2-h4')
        self.e3.setIPv6('2001:5::1/64' , 'e3-h5')
        self.e3.setIPv6('2001:6::1/64' , 'e3-h6')
        self.e4.setIPv6('2001:7::1/64' , 'e4-h7')
        self.e4.setIPv6('2001:8::1/64' , 'e4-h8')

        # Host

        self.h1.setIPv6('2001:1::2/64', 'eth0' , '2001:1::1')
        self.h2.setIPv6('2001:2::2/64', 'eth0' , '2001:2::1')
        self.h3.setIPv6('2001:3::2/64', 'eth0' , '2001:3::1')
        self.h4.setIPv6('2001:4::2/64', 'eth0' , '2001:4::1')
        self.h5.setIPv6('2001:5::2/64', 'eth0' , '2001:5::1')
        self.h6.setIPv6('2001:6::2/64', 'eth0' , '2001:6::1')
        self.h7.setIPv6('2001:7::2/64', 'eth0' , '2001:7::1')
        self.h8.setIPv6('2001:8::2/64', 'eth0' , '2001:8::1')

    def configIPv4s(self):
        self.c1.setIPv4('172.16.177.1/24', 'c1-e1')
        self.c1.setIPv4('172.16.178.1/24', 'c1-e2')
        self.c1.setIPv4('172.16.179.1/24', 'c1-e3')
        self.c1.setIPv4('172.16.180.1/24', 'c1-e4')

        self.c2.setIPv4('172.16.193.1/24', 'c2-e1')
        self.c2.setIPv4('172.16.194.1/24', 'c2-e2')
        self.c2.setIPv4('172.16.195.1/24', 'c2-e3')
        self.c2.setIPv4('172.16.196.1/24', 'c2-e4')

        self.e1.setIPv4('172.16.177.2/24' , 'e1-c1')
        self.e2.setIPv4('172.16.178.2/24' , 'e2-c1')
        self.e3.setIPv4('172.16.179.2/24' , 'e3-c1')
        self.e4.setIPv4('172.16.180.2/24' , 'e4-c1')

        self.e1.setIPv4('172.16.193.2/24' , 'e1-c2')
        self.e2.setIPv4('172.16.194.2/24' , 'e2-c2')
        self.e3.setIPv4('172.16.195.2/24' , 'e3-c2')
        self.e4.setIPv4('172.16.196.2/24' , 'e4-c2')

        # Edge to Host
        self.e1.setIPv4('172.16.1.1/24' , 'e1-h1')
        self.e1.setIPv4('172.16.2.1/24' , 'e1-h2')
        self.e2.setIPv4('172.16.3.1/24' , 'e2-h3')
        self.e2.setIPv4('172.16.4.1/24' , 'e2-h4')
        self.e3.setIPv4('172.16.5.1/24' , 'e3-h5')
        self.e3.setIPv4('172.16.6.1/24' , 'e3-h6')
        self.e4.setIPv4('172.16.7.1/24' , 'e4-h7')
        self.e4.setIPv4('172.16.8.1/24' , 'e4-h8')

        self.h1.setIPv4('172.16.1.2/24', 'eth0' , '172.16.1.1')
        self.h2.setIPv4('172.16.2.2/24', 'eth0' , '172.16.2.1')
        self.h3.setIPv4('172.16.3.2/24', 'eth0' , '172.16.3.1')
        self.h4.setIPv4('172.16.4.2/24', 'eth0' , '172.16.4.1')
        self.h5.setIPv4('172.16.5.2/24', 'eth0' , '172.16.5.1')
        self.h6.setIPv4('172.16.6.2/24', 'eth0' , '172.16.6.1')
        self.h7.setIPv4('172.16.7.2/24', 'eth0' , '172.16.7.1')
        self.h8.setIPv4('172.16.8.2/24', 'eth0' , '172.16.8.1')
        
    def configHosts(self):
        super().configHosts()
        self.c1 = self.getNodeByName('c1')
        self.c2 = self.getNodeByName('c2')
        self.e1 = self.getNodeByName('e1')
        self.e2 = self.getNodeByName('e2')
        self.e3 = self.getNodeByName('e3')
        self.e4 = self.getNodeByName('e4')
        self.h1 = self.getNodeByName('h1')
        self.h2 = self.getNodeByName('h2')
        self.h3 = self.getNodeByName('h3')
        self.h4 = self.getNodeByName('h4')
        self.h5 = self.getNodeByName('h5')
        self.h6 = self.getNodeByName('h6')
        self.h7 = self.getNodeByName('h7')
        self.h8 = self.getNodeByName('h8')
        self.configIPv4s()
        self.configIPv6s()
        

    def configRoutes(self):
        pass


class NetV6(Net):
    def __init__(self, *args, **kwargs):
        super().__init__(v='v6', *args, **kwargs)
        self.configRoutes()

    def configRoutes(self):
        self.e1.addSRv6Route('2001:3::/64' , ['2001:c1::1' , '2001:c2::2'], 'e1-c2')
        self.e1.addSRv6Route('2001:4::/64' , ['2001:b1::1' , '2001:b2::2'], 'e1-c1')
        self.e1.addSRv6Route('2001:5::/64' , ['2001:c1::1' , '2001:c3::2'], 'e1-c2')
        self.e1.addSRv6Route('2001:6::/64' , ['2001:b1::1' , '2001:b3::2'], 'e1-c1')
        self.e1.addSRv6Route('2001:7::/64' , ['2001:c1::1' , '2001:c4::2'], 'e1-c2')
        self.e1.addSRv6Route('2001:8::/64' , ['2001:b1::1' , '2001:b4::2'], 'e1-c1')

        self.e2.addSRv6Route('2001:1::/64' , ['2001:b2::1' , '2001:b1::2'], 'e2-c1')
        self.e2.addSRv6Route('2001:2::/64' , ['2001:c2::1' , '2001:c1::2'], 'e2-c2')
        self.e2.addSRv6Route('2001:5::/64' , ['2001:b2::1' , '2001:b3::2'], 'e2-c1')
        self.e2.addSRv6Route('2001:6::/64' , ['2001:c2::1' , '2001:c3::2'], 'e2-c2')
        self.e2.addSRv6Route('2001:7::/64' , ['2001:b2::1' , '2001:b4::2'], 'e2-c1')
        self.e2.addSRv6Route('2001:8::/64' , ['2001:c2::1' , '2001:c4::2'], 'e2-c2')

        self.e3.addSRv6Route('2001:1::/64' , ['2001:b3::1' , '2001:b1::2'], 'e3-c1')
        self.e3.addSRv6Route('2001:2::/64' , ['2001:c3::1' , '2001:c1::2'], 'e3-c2')
        self.e3.addSRv6Route('2001:3::/64' , ['2001:b3::1' , '2001:b2::2'], 'e3-c1')
        self.e3.addSRv6Route('2001:4::/64' , ['2001:c3::1' , '2001:c2::2'], 'e3-c2')
        self.e3.addSRv6Route('2001:7::/64' , ['2001:b3::1' , '2001:b4::2'], 'e3-c1')
        self.e3.addSRv6Route('2001:8::/64' , ['2001:c3::1' , '2001:c4::2'], 'e3-c2')

        self.e4.addSRv6Route('2001:1::/64' , ['2001:c4::1' , '2001:c1::2'], 'e4-c2')
        self.e4.addSRv6Route('2001:2::/64' , ['2001:b4::1' , '2001:b1::2'], 'e4-c1')
        self.e4.addSRv6Route('2001:3::/64' , ['2001:c4::1' , '2001:c2::2'], 'e4-c2')
        self.e4.addSRv6Route('2001:4::/64' , ['2001:b4::1' , '2001:b2::2'], 'e4-c1')
        self.e4.addSRv6Route('2001:5::/64' , ['2001:c4::1' , '2001:c3::2'], 'e4-c2')
        self.e4.addSRv6Route('2001:6::/64' , ['2001:b4::1' , '2001:b3::2'], 'e4-c1')


class NetV4(Net):
    def __init__(self, *args, **kwargs):
        super().__init__(v='v4', *args, **kwargs)
        self.configRoutes()
    
    def configRoutes(self):
        self.c1.vtysh_cmd(router_configs['c1'])
        self.c2.vtysh_cmd(router_configs['c2'])
        self.e1.vtysh_cmd(router_configs['e1'])
        self.e2.vtysh_cmd(router_configs['e2'])
        self.e3.vtysh_cmd(router_configs['e3'])
        self.e4.vtysh_cmd(router_configs['e4'])
    
    

if __name__ == '__main__':
    setLogLevel('info')
    net = NetV4()
    d = Dumps(*[net.getNodeByName(i) for i in ['h1','h2','h3','h4','h5','h6','h7','h8','e1','e2','e3','e4','c1']])
    net.start()
    CLI(net)
    d.terminate()
    net.stop()
    pass
    
    