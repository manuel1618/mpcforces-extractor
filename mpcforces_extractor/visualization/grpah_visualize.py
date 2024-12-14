from pyvis.network import Network
from mpcforces_extractor.datastructure.entities import Node, Element1D, Element
from mpcforces_extractor.datastructure.rigids import MPC
from mpcforces_extractor.datastructure.loads import SPCCluster
from mpcforces_extractor.datastructure.subcases import Subcase
from mpcforces_extractor.force_extractor import (
    MPCForceExtractor,
    SPCForcesExtractor,
    FEMExtractor,
)


class GrpahVisualize:
    """
    This class is used to visualize the graph (Elements, Parts, Nodes, MPCs)
    """

    def __init__(self):
        self.net = Network()
        self.node_id2node = {}
        self.__build_nodes()
        self.__build_edges()

    def __build_nodes(self):
        """
        This method is used to build the nodes of the grpah (Nodes, Parts)
        """
        nodes = MPC.get_all_node_ids()
        for node in nodes:
            self.__add_node(node, f"Node: {node}", f"{node}")
            self.node_id2node[node] = Node.node_id2node[node]

        for part in MPC.get_all_part_ids():
            self.__add_node(part, f"Part: {part}", f"{part}")

    def __build_edges(self):
        """
        This method is used to build the edges of the graph (MPC-Node, Part-Node)
        """
        for rbe in MPC.get_all_mpcs():
            for node in rbe.nodes:
                self.__add_edge(rbe.master_node.id, node.id)

        for mpc in MPC.get_all_mpcs():
            for part_id, nodes in mpc.part_id2node_ids.items():
                for node_id in nodes:
                    if node_id in self.node_id2node:
                        self.__add_edge(part_id, node_id)

    def __add_node(self, node_id, label, hover_info):
        """
        Adds a node to the grpah
        """
        self.net.add_node(node_id, label=label, title=hover_info)

    def __add_edge(self, node1, node2):
        """
        Adds an edge to the graph
        """
        self.net.add_edge(node1, node2)

    def save_graph(self, path):
        """
        Saves the graph to a file
        """
        self.net.save_graph(path)

    def show(self, path):
        """
        Shows the graph in the browser
        """
        self.net.show(path, notebook=False)


def main():
    """
    Test Method
    """

    input_folder = "data/input"
    # output_folder = "data/output"
    model_name = "m"
    # model_name = "Flange"
    blocksize = 8

    # Clear all Instances (important)
    Node.reset()
    Element1D.reset()
    Element.reset_graph()
    Subcase.reset()
    MPC.reset()

    fem_extractor = FEMExtractor(
        input_folder + f"/{model_name}.fem", block_size=blocksize
    )
    fem_extractor.build_fem_data()
    mpc_force_extractor = MPCForceExtractor(input_folder + f"/{model_name}.mpcf")
    mpc_force_extractor.build_subcase_data()
    spc_forces_extractor = SPCForcesExtractor(input_folder + f"/{model_name}.spcf")
    spc_forces_extractor.build_subcase_data()

    SPCCluster.build_spc_cluster()
    SPCCluster.calculate_force_sum()

    # hmm
    for mpc in MPC.get_all_mpcs():
        mpc.get_subcase_id2part_id2force()

    graph = GrpahVisualize()
    graph.show("graph.html")


if __name__ == "__main__":
    main()
