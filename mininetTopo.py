'''
Please add your name: Tan Wei Adam
Please add your matric number: A0180277B
'''

import os
import sys
import atexit
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.link import Link
from mininet.node import RemoteController

net = None

class TreeTopo(Topo):
			
	def __init__(self):
		# Initialize topology
		Topo.__init__(self)
		self.hostList = {}
		self.switchList = {}
		self.linkInfo = {} 
		self.createNodes("topology.in")    
	def createNodes(self, inFile):
		with open(inFile) as nodeParams:
			linkList = []
			hosts, switches, links = nodeParams.readline().split()
			for i in range(int(links)):
				linkList.append(nodeParams.readline().split(','))
			# You can write other functions as you need.

			# Add hosts
		    # > self.addHost('h%d' % [HOST NUMBER])
		    	for i in range(int(hosts)):
		    		hostname = 'h%d' % (i+1)
		    		self.hostList[hostname] = self.addHost(hostname)
		    		self.linkInfo[hostname] = {}
		    		

			# Add switches
		    # > sconfig = {'dpid': "%016x" % [SWITCH NUMBER]}
		    # > self.addSwitch('s%d' % [SWITCH NUMBER], **sconfig)
		    	for i in range(int(switches)):
		    		switchname = 's%d' % (i+1)
		    		sconfig = {'dpid': "%016x" % (i+1)}
		    		self.switchList[switchname] = self.addSwitch(switchname, **sconfig)
		    		self.linkInfo[switchname] = {}

			# Add links
			# > self.addLink([HOST1], [HOST2])
			
			for lnk in linkList:
				hostA = lnk[0]
				hostB = lnk[1]
				linkbw = int(lnk[2])
				self.addLink(hostA, hostB)
				self.linkInfo[hostA][hostB] = linkbw
				self.linkInfo[hostB][hostA] = linkbw
def QOSConfig(net, topo):
	for switch in net.switches:
		for intf in switch.intfList():
			if intf.link:
				node1 = intf.link.intf1.node
				node2 = intf.link.intf2.node
				tar = node1
				if node1 == switch:
					tar = node2
				interface = intf.link.intf2
				if node1 == switch:
					interface = intf.link.intf1
				bw = topo.linkInfo[switch.name][tar.name]
				QOSHelper(interface.name, bw, tar, net)
				
def QOSHelper(interface_name, bw, tar, net):
	bw = bw * 1000000
	X = 0.8 * bw
	
	Y = 0.5 * bw
	os.system('sudo ovs-vsctl -- set Port %s qos=@newqos \
	-- --id=@newqos create QoS type=linux-htb other-config:max-rate=%d queues=0=@q0,1=@q1,2=@q2 \
	-- --id=@q0 create queue other-config:max-rate=%d other-config:min-rate=%d\
	-- --id=@q1 create queue other-config:min-rate=%d \
	-- --id=@q2 create queue other-config:max-rate=%d' % (interface_name, bw, X, Y, X, Y))
				

def startNetwork():
    info('** Creating the tree network\n')
    
    inFile = "topology.in"
    
    
    topo = TreeTopo()

    global net
    net = Mininet(topo=topo, link = Link,
                  controller=lambda name: RemoteController(name, ip='192.168.56.103'),
                  listenPort=6633, autoSetMacs=True)

    info('** Starting the network\n')
    net.start()

    # Create QoS Queues
    # > os.system('sudo ovs-vsctl -- set Port [INTERFACE] qos=@newqos \
    #            -- --id=@newqos create QoS type=linux-htb other-config:max-rate=[LINK SPEED] queues=0=@q0,1=@q1,2=@q2 \
    #            -- --id=@q0 create queue other-config:max-rate=[LINK SPEED] other-config:min-rate=[LINK SPEED] \
    #            -- --id=@q1 create queue other-config:min-rate=[X] \
    #            -- --id=@q2 create queue other-config:max-rate=[Y]')
    
    QOSConfig(net, topo)

    info('** Running CLI\n')
    CLI(net)

def stopNetwork():
    if net is not None:
        net.stop()
        # Remove QoS and Queues
        os.system('sudo ovs-vsctl --all destroy Qos')
        os.system('sudo ovs-vsctl --all destroy Queue')


if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()
