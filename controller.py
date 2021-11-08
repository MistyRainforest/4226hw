'''
Please add your name: Tan Wei Adam
Please add your matric number: A0180277B
'''

import sys
import os
from sets import Set
import datetime as DT

from pox.core import core

import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_forest

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.addresses import IPAddr, EthAddr

log = core.getLogger()

TIMEOUT = 25
HIGH = 1
MED = 0
LOW = 2
FIREWALL = 200
QOS_PRIORITY = 100

class Controller(EventMixin):
    def __init__(self):
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)
        self.maclist = {}
	self.ttllist = {}
	self.service_level = {}

        
    # You can write other functions as you need.
    def _handle_PacketIn (self, event):    
    	# install entries to the route table
        def install_enqueue(event, packet, outport, q_id):
        	msg = of.ofp_flow_mod()
        	msg.match = of.ofp_match.from_packet(packet, port_in)
        	msg.priority = QOS_PRIORITY
        	msg.actions.append(of.ofp_action_enqueue(port = outport, queue_id = q_id))
        	log.debug("qid: %d" % q_id)
        	msg.data = event.ofp
        	msg.idle_timeout = TIMEOUT
        	msg.hard_timeout = TIMEOUT
        	event.connection.send(msg)
        	return
        	
        def get_qid(source, dest):
	    	source = str(source)
	    	dest = str(dest)
	    	if get_qidip(source) == HIGH or get_qidip(dest) == HIGH:
	    		return HIGH
	    	if get_qidip(source) == MED or get_qidip(dest) == MED:
	    		return MED
	    	return LOW
	def get_qidip(ip):
		if ip is None:
			return MED
	    	if ip not in self.service_level:
	    		return LOW
	    	else:
	    		return self.service_level[ip]
	def learn(): 
		if dpid not in self.maclist:
			self.maclist[dpid] = {}
			self.ttllist[dpid] = {}
		if source_mac not in self.maclist[dpid]:
			self.maclist[dpid][source_mac] = port_in
			self.ttllist[dpid][source_mac] = DT.datetime.now()
	def forget():
		if dest_mac in self.ttllist[dpid] and self.ttllist[dpid][dest_mac] + DT.timedelta(seconds=TIMEOUT) <= DT.datetime.now():
			self.maclist[dpid].pop(dest_mac)
			self.ttllist[dpid].pop(dest_mac)

    	# Check the packet and decide how to route the packet
        def forward(message = None):
        	if dest_mac.is_multicast:
        		return flood("Multicast->Flood at switch %s" % dpid)
        	if dest_mac not in self.maclist[dpid]:
        		return flood("Unknown->Flood at switch %s" % dpid)
        	q_id = get_qid(source_ip, dest_ip)
        	outport = self.maclist[dpid][dest_mac]
        	install_enqueue(event, packet, outport, q_id)


        # When it knows nothing about the destination, flood but don't install the rule
        def flood (message = None):
            # define your message here
            log.debug(message)
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.in_port = port_in
            msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))
            event.connection.send(msg)
            log.debug("At switch: %s: Flooding destination %s" % (dpid, dest_ip))

            # ofp_action_output: forwarding packets out of a physical or virtual port
            # OFPP_FLOOD: output all openflow ports expect the input port and those with 
            #    flooding disabled via the OFPPC_NO_FLOOD port config bit
            # msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        def map_ip_mac(ip):
        	id = int(str(ip).split('.')[-1])
        	mac = EthAddr("%012x" % (id & 0xffffffffffff,))
        	return mac
        packet = event.parsed
        source_mac = packet.src
        dest_mac = packet.dst
        source_ip = None
        dest_ip = None
        port_in = event.port
        dpid = event.dpid
        if packet.type == packet.ARP_TYPE:
        	dest_ip = packet.payload.protodst
        	source_ip = packet.payload.protosrc
        	if dest_mac.is_multicast:
        		dest_mac = map_ip_mac(dest_ip)
        elif packet.type == packet.IP_TYPE:
        	dest_ip = packet.payload.dstip
        	source_ip = packet.payload.srcip
        	
        learn()
        forward()
        forget()

        


    def _handle_ConnectionUp(self, event):
        dpid = dpid_to_str(event.dpid)
        log.debug("Switch %s has come up.", dpid)
        
        def helper(filename):
        	firewall_policies = []
        	with open(filename) as f:
        		rules_num, premium_host_num = f.readline().split()
        		for i in range(int(rules_num)):
        			rules = [part.strip() for part in f.readline().strip().split(',')]
        			if len(rules) == 3:
        				firewall_policies.append((rules[0], rules[1], rules[2]))
        			elif len(rules) == 2:
        				firewall_policies.append((rules[0], rules[1]))
        		for i in range(int(premium_host_num)):
        			prem_ip = f.readline().strip()
        			self.service_level[prem_ip] = HIGH
        	return firewall_policies
        
        # Send the firewall policies to the switch
        def sendFirewallPolicy(connection, policy):
        	msg = of.ofp_flow_mod()
        	msg.match.dl_type = 0x0800
        	msg.match.nw_proto = 6
        	
        	if len(policy) == 2:
        		dest_ip, dest_port = policy
        		source_ip = None
        	elif len(policy) == 3:
        		source_ip, dest_ip, dest_port = policy
        	msg.match.nw_dst = IPAddr(dest_ip)
        	msg.match.tp_dst = int(dest_port)
        	if source_ip:
        		msg.match.nw_src = IPAddr(source_ip)
        	#msg.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
        	
        		
        	connection.send(msg)
        	return
            # define your message here
            
            # OFPP_NONE: outputting to nowhere
            # msg.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
	firewall_policies = helper("./pox/misc/policy.in")
        for policy in firewall_policies:
            sendFirewallPolicy(event.connection, policy)
            

def launch():
    # Run discovery and spanning tree modules
    pox.openflow.discovery.launch()
    pox.openflow.spanning_forest.launch()

    # Starting the controller module
    core.registerNew(Controller)
