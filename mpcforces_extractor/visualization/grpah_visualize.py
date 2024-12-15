from enum import Enum
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


class NodeType(Enum):
    """
    used for transform ids to graph ids
    """

    NODE = 1
    PART = 2
    MPC = 3


class GrpahVisualizer:
    """
    This class is used to visualize the graph (Elements, Parts, Nodes, MPCs)
    """

    def __init__(self):
        self.net = Network(select_menu=True, notebook=False)
        self.net.repulsion()
        self.__build_nodes()
        self.__build_edges()

    def __build_nodes(self):
        """
        This method is used to build the nodes of the grpah (Nodes, Parts)
        """
        for part in MPC.get_all_part_ids():
            part_graph_id = GrpahVisualizer.to_graph_id(part, NodeType.PART)
            self.__add_vertex(part_graph_id, f"Part: {part}", f"{part}")

        for mpc in MPC.get_all_mpcs():
            mpc_graph_id = GrpahVisualizer.to_graph_id(mpc.master_node.id, NodeType.MPC)
            hover_info = f"master: {mpc.master_node.id}\n slaves: {len(mpc.nodes)}\n"
            self.__add_vertex(mpc_graph_id, f"MPC: {mpc.master_node.id}", hover_info)
            self.__append_to_vertex_hover(mpc_graph_id, "temp")

    def __build_edges(self):
        """
        This method is used to build the edges of the graph (MPC-Node, Part-Node)
        """
        for mpc in MPC.get_all_mpcs():
            for part_id, _ in mpc.part_id2node_ids.items():
                part_grpah_id = GrpahVisualizer.to_graph_id(part_id, NodeType.PART)
                mpc_graph_id = GrpahVisualizer.to_graph_id(
                    mpc.master_node.id, NodeType.MPC
                )
                self.__add_edge(part_grpah_id, mpc_graph_id)

    @staticmethod
    def to_graph_id(my_id, node_type):
        """
        Converts the id to a graph id
        """
        if node_type == NodeType.NODE:
            return f"{my_id}"
        return f"{node_type.name}_{my_id}"

    def __add_vertex(self, node_id, label, hover_info):
        """
        Adds a node to the grpah
        """
        self.net.add_node(node_id, label=label, title=hover_info)

    def __append_to_vertex_hover(self, vertex_id, text):
        """
        Adds a title (hover info) to the vertex
        """
        self.net.get_node(vertex_id)["title"] += f"\n{text}"

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
        # Enable filter menu for nodes
        self.net.show_buttons(
            filter_=["selection", "physics"]
        )  # This will show a filter menu for nodes

        self.net.show(path, notebook=False)


def main():
    """
    Test Method
    """

    input_folder = "data/input"
    # output_folder = "data/output"
    model_name = "flange"
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

    graph = GrpahVisualizer()
    graph.show("graph.html")


if __name__ == "__main__":
    main()
