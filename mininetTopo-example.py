import os
import sys
import atexit
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.link import Link
from mininet.node import RemoteController
from mininet.util import dumpNodeConnections

net = None

class SingleSwitchTopo(Topo):

    def __init__(self, n=2):
        # Initialize topology
        Topo.__init__(self)
        # You can write other functions as you need.

        # Add hosts
        # > self.addHost('h%d' % [HOST NUMBER])

        # Add switches
        # > sconfig = {'dpid': "%016x" % [SWITCH NUMBER]}
        # > self.addSwitch('s%d' % [SWITCH NUMBER], **sconfig)

        # Add links
        # > self.addLink([HOST1], [HOST2])

        switch = self.addSwitch('s1')
        for h in range(n):
            host = self.addHost('h%s' % (h+1))
            self.addLink(host, switch)
        print self.links(True, False, True)


def startNetwork():
    info('** Creating the tree network\n')
    topo = SingleSwitchTopo(n=4)

    global net
    # modify the ip address if you are using a remote pox controller
    net = Mininet(topo=topo, link = Link,
                  controller=lambda name: RemoteController(name, ip='127.0.0.1'),
                  listenPort=6633, autoSetMacs=True)


    info('** Starting the network\n')
    net.start()

    # Create QoS Queues
    # > os.system('sudo ovs-vsctl -- set Port [INTERFACE] qos=@newqos \
    #            -- --id=@newqos create QoS type=linux-htb other-config:max-rate=[LINK SPEED] queues=0=@q0,1=@q1,2=@q2 \
    #            -- --id=@q0 create queue other-config:max-rate=[LINK SPEED] other-config:min-rate=[LINK SPEED] \
    #            -- --id=@q1 create queue other-config:min-rate=[X] \
    #            -- --id=@q2 create queue other-config:max-rate=[Y]')

    info('** Running CLI\n')
    CLI(net)

def perfTest():
    info('** Creating network and run simple performance test\n')
    topo = SingleSwitchTopo(n=4)
    # modify the ip address if you are using a remote pox controller
    net = Mininet(topo=topo, link=Link,
                  controller=lambda name: RemoteController(name, ip='127.0.0.1'),
                  listenPort=6633, autoSetMacs=True)
    net.start()
    info("Dumping host connections")
    dumpNodeConnections(net.hosts)
    info("Testing network connectivity")
    net.pingAll()

    h1, h4 = net.get('h1', 'h4')

    info("Testing connectivity between h1 and h4")
    net.ping((h1,h4))
    info("Testing bandwidth between h1 and h4")
    net.iperf((h1,h4),port=8080)
    net.stop()

def stopNetwork():
    if net is not None:
        net.stop()
        # Remove QoS and Queues
        # os.system('sudo ovs-vsctl --all destroy Qos')
        # os.system('sudo ovs-vsctl --all destroy Queue')


if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    # run option1: start some basic test on your topology such as pingall, ping and iperf.
    perfTest()
    # run option2: start a command line to explore more of mininet, you can try different commands.
    # startNetwork()