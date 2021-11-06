from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_tree

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.addresses import IPAddr, EthAddr

log = core.getLogger()

class SimpleController(EventMixin):
    def __init__(self):
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        dpid = event.dpid
        src = packet.src
        dst = packet.dst
        inport = event.port

        # ofp_flow_mod: flow table modification
        msg = of.ofp_flow_mod()
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        event.connection.send(msg)

        # ofp_packet_out: sending packets from the switch, will not modify the flow table
        # msg = of.ofp_packet_out()
        # msg.data = event.ofp
        # msg.in_port = inport
        # msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        # event.connection.send(msg)
        log.info("# S%i: Message sent: Outport %i\n", dpid, of.OFPP_FLOOD)


    def _handle_ConnectionUp(self, event):
        log.info("Switch %s has come up.", dpid_to_str(event.dpid))

def launch ():
    # Run discovery and spanning tree modules
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    # Starting the controller module
    core.registerNew(SimpleController)