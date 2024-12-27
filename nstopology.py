import pprint
from nest.topology import network, Router, Node, Switch, connect
from nest.routing.routing_helper import RoutingHelper
from nest.topology.address_helper import AddressHelper
from nest.routing.zebra import Zebra
import networkx as nx
import matplotlib.pyplot as plt 

class GDevice:
    def __init__(self, name, ports, role):
        self.name = name
        self.ports = ports
        self.role = role
        self.connections = {}
        self.ns_node_ref = None

    def add_link(self, dest, srcif, destif):
        self.connections[dest] = [srcif, destif]

    def add_ns_ref(self, ns_ref):
        self.ns_node_ref = ns_ref

    def ns_ref(self):
        return self.ns_node_ref
    
    def set_role(self, role):
        self.role = role

    def show(self):
        print("Node: %s ports#: %s type %s" %
                (self.name,self.ports, self.role))
        #print(" connections:")
        for k,v in self.connections.items():
            print(f"   %s.%s--> %s.%s" %
                (self.name, v[0], k, v[1]))

class NSTopology:
    def __init__(self, tname=None):
        self.topoId = tname
        self.tgraph = {}  # maintain interfaces and node connection
        self.interfaces = {}

    def plot(self):

        G = nx.Graph()
        color_map = []
        for node, neig  in self.tgraph.items():
            G.add_node(node, color = 'red', )
            if node == "Spine":
                color_map.append('blue')
                G.nodes[node]["layer"] = 1
            elif node == "Leaf":
                color_map.append('green')  
                G.nodes[node]["layer"] = 2
            else:
                color_map.append('grey')  
                G.nodes[node]["layer"] = 3
                
            for k,v in neig.connections.items():
                G.add_edge(node, k)
        nx.draw_spring(G, node_color=color_map,
                       with_labels = True)
        plt.savefig('plot.png')

    def add_router(self, rtrname="rtr", rid=None, role="router"):
        if rid != None:
            rname = rtrname + str(rid)
        else:
            rname = rtrname

        new_node = GDevice(rname, 0, role)
        self.tgraph[rname] = new_node
        ns_ref = Router(rname)
        new_node.add_ns_ref(ns_ref)
        return new_node

    def add_switch(self, swname="sw", rid = None):
        if rid != None:
            rname = swname + str(rid)
        else:
            rname = swname

        new_node = GDevice(swname, 0, 'switch')
        self.tgraph[swname] = new_node
        ns_ref = Router(rname)
        new_node.add_ns_ref(ns_ref)
        return new_node

    def add_host(self, hname, role):
        new_node = GDevice(hname, 0, role)
        self.tgraph[hname] = new_node
        ns_ref = Node(hname)
        new_node.add_ns_ref(ns_ref)
        return new_node

    def add_link(self, ep1, ep2, ep1_ep2_ifname=None, ep2_ep1_ifname=None):
        # assert ep1 and ep2 exist
        if ep1_ep2_ifname is None:
            ep1_ep2_ifname = ep1.name + "_" + ep2.name
        if ep2_ep1_ifname is None:
            ep2_ep1_ifname = ep2.name + "_" + ep1.name

        #Create interfaces
        r1 = self.get_ns_ref(ep1)
        r2 = self.get_ns_ref(ep2)
        (if1, if2) = connect(r1, r2,
                            ep1_ep2_ifname,
                            ep2_ep1_ifname)

        self.interfaces[ep1] = {ep1_ep2_ifname, if1}
        self.interfaces[ep2] = {ep2_ep1_ifname, if2}

        src_node = self.get_node(ep1)
        dst_node = self.get_node(ep2)
        src_node.add_link(ep2, ep1_ep2_ifname, ep2_ep1_ifname)
        dst_node.add_link(ep1, ep2_ep1_ifname, ep1_ep2_ifname)

    def get_node(self, nname):
        gnode = None
        if nname in self.tgraph:
            gnode = self.tgraph[nname]
        return gnode

    def get_ns_ref(self, nname):
        ns_ref = None
        if nname in self.tgraph.keys():
            ns_ref = self.tgraph[nname].ns_node_ref
        else:
            print("NS_REF not found for node ", nname)
        return ns_ref

    def show_nodes(self):
        for v in self.tgraph.values():
            v.show()

    def show_ifs(self):
        for k,v in self.interfaces.items():
            for ifname in v.keys():
                print(k, "-->", ifname)

