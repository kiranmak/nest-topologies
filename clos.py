import matplotlib.pyplot as plt
import networkx as nx
from nstopology import NSTopology as nstopo

subset_color = [
    "lightgreen",
    "lightblue",
    "pink",
    "darkorange",
]

class CLOS(nstopo):
    pe_routers = {}
    p_routers = {}
    servers = {}
    def __init__(self, nspines=1, nleaves=2, nservers_pe=1):
        super(CLOS, self).__init__(tname="CLOS")
        self.nspines = nspines
        self.nleaves = nleaves
        self.nsvrs = nservers_pe
        self.launch_ns(nspines, nleaves, nservers_pe)

    def launch_ns(self, nsp, npe, nservers_pe):
        # create spine routers
        for i in range(nsp):
            p_key = "P" + str(i)
            self.p_routers[p_key] = super(
                    CLOS, self).add_router(p_key, None, "Spine")
            self.p_routers[p_key].ports = npe

        # number of pe
        for i in range(npe):
            p_key = "PE" + str(i)
            self.pe_routers[p_key] = super(
                    CLOS, self).add_router(p_key, None, "Leaf")
            self.pe_routers[p_key].ports = nsp + nservers_pe

            # number of servers per pe
            for j in range(nservers_pe):
                hname = "h" + str(i) + str(j)
                self.servers[hname] = super(
                        CLOS, self).add_host(hname, "Server")
                self.servers[hname].ports = 1

        # k is router name and v is Gnode of it.
        for p, k in enumerate(self.p_routers.keys()):
            p_port = 0
            for pe, pe_k in enumerate(self.pe_routers.keys()):
                ifname1 = "Gi" + str(p_port)
                ifname2 = "Gi" + str(p)
                super(CLOS, self).add_link(
                    k , pe_k, ifname1, ifname2)
                p_port += 1

        for pe, (pe_k, pe_v) in enumerate(self.pe_routers.items()):
            pe_port = 0
            for j in range(self.nsvrs):
                hname = "h" + str(pe) + str(j)
                ifname1 = "eth" + str(pe_port)
                ifname2 = "eth" + str(0)

                super(CLOS, self).add_link(
                    pe_k, hname, ifname1, ifname2)
                pe_port += 1

    def multilayered_graph(self):
        spines = list(self.p_routers.keys())
        leaves = list(self.pe_routers.keys())
        servers = list(self.servers.keys())

        layers = [servers, leaves, spines]
        G = nx.DiGraph()
        for i, layr in enumerate(layers):
            G.add_nodes_from(layr, color=subset_color[i], layer= i)

        for i in range(0, len(leaves)):
            for j in range(0, len(spines)):
                G.add_edge(layers[1][i], layers[2][j])

        for j in range(0, len(leaves)):
            for k in range(0, self.nsvrs):
                index = j * self.nsvrs + k
                G.add_edge(layers[1][j], layers[0][index])

        return G

    def plot_topo(self):
        G = self.multilayered_graph()
        color = [subset_color[data["layer"]] for v, data in G.nodes(data=True)]
        pos = nx.multipartite_layout(G, subset_key="layer", align="horizontal")
        plt.figure(figsize=(14, 14))
        
        nx.draw(G, pos, edge_color='gray', with_labels=True, node_color=color, node_size=800)
        plt.axis("equal")
        plt.savefig('spineleaf.png')
        plt.show()

clos = CLOS(3, 4, 2)
clos.plot_topo()