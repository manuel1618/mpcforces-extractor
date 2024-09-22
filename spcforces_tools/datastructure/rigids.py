from typing import Dict, List
import time
import matplotlib.pyplot as plt
import networkx as nx
from spcforces_tools.datastructure.entities import Node, Element


class MPC:
    """
    This class is a Multiple Point Constraint (MPC) class that is used to store the nodes and the dofs
    """

    def __init__(self, element_id: int, master_node: Node, nodes: List, dofs: str):
        self.element_id: int = element_id
        if master_node is None:
            print("Master_node2coords is None for element_id", element_id)
        self.master_node = master_node
        self.nodes: List = nodes
        self.dofs: int = dofs
        self.part_id2force = {}
        self.part_id2node_ids = {}

    def get_part_id2node_ids(self, node_stack: List) -> Dict:
        """
        Gets the connected nodes for each part (attached elements) via neighbors
        """

        part_id2node_ids = {}

        part_id = 1
        while len(node_stack) > 0:
            node = node_stack.pop()
            element = node.connected_elements[0]
            connected_nodes = element.get_all_connected_nodes()
            part_nodes = set(connected_nodes).intersection(self.nodes)
            for node_temp in part_nodes:
                if node_temp in node_stack:
                    node_stack.remove(node_temp)
            part_id2node_ids[part_id] = [node.id for node in part_nodes]
            part_id += 1

        return part_id2node_ids

    def get_part_id2node_ids_graph(self, slave_nodes: List) -> Dict:
        """
        This method is used to get the part_id2node_ids using the graph
        """

        start_time = time.time()
        print("Building the part_id2node_ids using the graph")
        part_id2node_ids = {}
        graph = Element.graph.copy()

        print("...Caluclatiung Sub Graph")
        sub_graph = graph.subgraph(slave_nodes)

        # visualize the graph
        pos = nx.spring_layout(sub_graph)
        nx.draw(
            sub_graph,
            pos=pos,
            with_labels=True,
            labels={node: node.id for node in sub_graph.nodes()},
        )
        # plt.show()
        plt.savefig("data/output/sub_graph.png")

        print("...Calculating connected components")
        connected_components = list(nx.connected_components(sub_graph))

        # debug write this to a file
        # def stringizer(node):
        # return str(node.id)
        # nx.write_gml(sub_graph, "data/output/sub_graph.gml", stringizer)

        print(
            "Finished calculating the connected components, returning part_id2node_ids"
        )
        print("..took ", round(time.time() - start_time, 2), "seconds")

        for i, connected_component in enumerate(connected_components):
            part_id2node_ids[i + 1] = [node.id for node in connected_component]

        return part_id2node_ids

    def sum_forces_by_connected_parts(
        self, node_id2force: Dict, use_graph: bool
    ) -> Dict:
        """
        This method is used to sum the forces by connected - parts NEW
        """
        forces = {}

        slave_nodes = self.nodes.copy()

        if use_graph:
            self.part_id2node_ids = self.get_part_id2node_ids_graph(slave_nodes)
        else:
            self.part_id2node_ids = self.get_part_id2node_ids(slave_nodes)

        # add the forces for each part
        for part_id, node_ids in self.part_id2node_ids.items():

            forces[part_id] = [0, 0, 0, 0, 0, 0]

            for node_id in node_ids:
                if node_id not in node_id2force:
                    print(
                        f"Node {node_id} not found in the MPC forces file - bug or zero - you decide!"
                    )
                    continue

                force = node_id2force[node_id]
                force_x = force[0]
                force_y = force[1]
                force_z = force[2]
                moment_x = force[3]
                moment_y = force[4]
                moment_z = force[5]

                forces[part_id][0] += force_x
                forces[part_id][1] += force_y
                forces[part_id][2] += force_z
                forces[part_id][3] += moment_x
                forces[part_id][4] += moment_y
                forces[part_id][5] += moment_z

        self.part_id2force = forces
        return forces
