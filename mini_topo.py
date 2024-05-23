from mininet.topo import Topo
from base import IntelV6Host
from main import Dumps
from mininet.node import DefaultController, Host, OVSBridge, OVSKernelSwitch
from mininet.link import Intf, Link, OVSLink
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel

class MiniTopo(Topo):

    def __init__(self, *args, **params):
        super().__init__(*args, **params)

        self.addHost('h1' , cls=IntelV6Host, ip=None)
        self.addHost('h2', cls=IntelV6Host, ip=None)

        self.addSwitch('s1' , cls=OVSBridge)

        self.addLink('h1', 's1', cls=OVSLink , intfName1='eth0', intfName2='s1-h1')
        self.addLink('h2', 's1', cls=OVSLink , intfName1='eth0', intfName2='s1-h2')


class SimpleNet(Mininet):

    def __init__(self, *args, **kwargs):
        super().__init__(topo=MiniTopo() , controller=None , *args , **kwargs)
        self.__configIp()
    
    def __configIp(self):
        h1: IntelV6Host = self.getNodeByName('h1')
        h2: IntelV6Host = self.getNodeByName('h2')
        h1.setIPv6('2001:1::1/64')
        h2.setIPv6('2001:1::2/64')
        h1.setIPv4('192.168.1.1/24', intf='eth0')
        h2.setIPv4('192.168.1.2/24', intf='eth0')

if __name__ == '__main__':
    setLogLevel('info')
    net = SimpleNet()
    net.start()
    h1 = net.getNodeByName('h1')
    h2 = net.getNodeByName('h2')
    r = Dumps(h1, h2)
    CLI(net)
    r.terminate()
    net.stop()
    pass