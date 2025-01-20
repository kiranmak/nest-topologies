import os
import matplotlib.pyplot as plt
import networkx as nx
import pydot
from PIL import Image
from nstopology import NSTopology as nstopo

subset_color = [
    "lightgreen",
    "lightblue",
    "pink",
    "darkorange",
]

class H2H(nstopo):
    servers = {}
    def __init__(self, nservers=2, delns=False):
        super(H2H, self).__init__(tname="H2H", delns=delns)
        self.nsvrs = nservers

        self.launch_ns(nservers)
        #self.auto_addr_assign()
        #print(f"Addresses Assigned!")

    def launch_ns(self, nservers):

        # number of servers per edge-router
        left_edge  = "h1"  #"h" + str(0)
        right_edge = "h2"  #"h" + str(1)
        self.servers[left_edge] = self.add_host(left_edge, "Server")
        self.servers[right_edge] = self.add_host(right_edge, "Server")
        a = self.get_ns_ref(left_edge)
        b = self.get_ns_ref(right_edge)

        self.servers[left_edge].ports = 1
        self.servers[right_edge].ports = 1

        subnet = self.create_network("eth1", "192.168.0.16", 28, 0)
        self.add_link(left_edge, right_edge, "eth0", subnet)
        '''
        print("nodes = ", self.servers.keys())
        print("Make links")
        from nest.topology.network import Network
        from nest.topology.connect import connect
        from nest.topology.address_helper import AddressHelper
        mask = 28
        pnet = Network("192.168.1.16" + "/" + str(mask))
        (if1, if2) = connect(a, b, "eth0", "eth1", pnet)
        with pnet:
            AddressHelper.assign_addresses()
        '''

    def get_edges(self):

        nodes = [d.get('src') for d in self.interfaces]
        other_nodes = [d.get('dst') for d in self.interfaces]
        return nodes, other_nodes

    def multilayered_graph(self):

        snames = list(self.servers.keys())
        layers = [snames]
        sizes = [500, 700]
        G = nx.Graph()

        for i, node in enumerate(layers):
            G.add_nodes_from(node, color=subset_color[i], size=sizes[i])

        from_nodes, to_nodes = self.get_edges()
        for i, from_node in enumerate(from_nodes):
            G.add_edge(from_node, to_nodes[i])

        # Analyze the graph
        print("Nodes:", G.nodes)
        print("Edges:", G.edges)
        return G

    def plot_topo(self):

        # Step 1: get nodes and edges graph
        G = self.multilayered_graph()

        # Step 2: Define positions for nodes in a horizontal line
        positions = nx.spring_layout(G)


        # Print the positions of each node
        print("Node Positions:")
        for node, pos in positions.items():
            pos[1] = 0
            #print(f"Node {node}: {pos}")

        # Step 3: Draw the graph
        node_clrs = [data['color'] for _, data in G.nodes(data=True)]
        node_szs = [data['size'] for _, data in G.nodes(data=True)]
        plt.figure(figsize=(8, 2))  # Adjust figure size for horizontal alignment
        nx.draw(G, positions, with_labels=True, node_color=node_clrs, node_size=node_szs, edge_color='gray')
        #plt.show()

        plt.title("Custom Straight Line Layout")
        fname = self.out_folder + "point-to-point.png"
        # Join paths
        fname = os.path.join(self.out_folder, "point-to-point.png")
        print(fname)  # Output:

        plt.savefig(fname)
        plt.close()
        nx.drawing.nx_pydot.write_dot(G, fname + ".dot")

        # Display the saved image
        #img = Image.open(fname)
        #img.show()


    def plot_topo2(self):

        G = self.multilayered_graph()
        color = [data["color"] for v, data in G.nodes(data=True)]

        pos   = nx.multipartite_layout(G,
                                        subset_key="layer",
                                        align="horizontal")
        # Draw the graph with the custom layout
        nx.draw(G, pos, with_labels=True,
                arrows=True, node_color=color, node_size=800)
        plt.title("Custom Straight Line Layout")

        plt.savefig(self.out_folder + 'point-to-point.png')
        nx.drawing.nx_pydot.write_dot(
                G, self.out_folder  + "point-to-point.dot")
        #plt.show()


h2h = H2H(2, False)
h2h.show_nodes()
