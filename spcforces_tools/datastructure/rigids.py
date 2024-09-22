from typing import Dict, List
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
        self.part_id2slave_node_ids = {}

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
        part_id2node_ids = {}
        graph = Element.graph
        sub_graph = graph.subgraph(slave_nodes)

        # visualize the graph
        # nx.draw(sub_graph, with_labels=True)
        # plt.show()

        connected_components = list(nx.connected_components(sub_graph))

        # merge the connected components if they are linked in the graph
        comps_to_remove = []
        for i, comp in enumerate(connected_components):
            if comp in comps_to_remove:
                continue
            node1 = list(comp)[0]
            for _, comp2 in enumerate(connected_components):
                if comp == comp2:
                    continue
                if comp2 in comps_to_remove:
                    continue
                node2 = list(comp2)[0]
                # check if we can trvael from one component to another in the graph
                if nx.has_path(graph, node1, node2):
                    connected_components[i] = comp.union(comp2)
                    comps_to_remove.append(comp2)
        # remove the empty components
        connected_components = [
            comp for comp in connected_components if comp not in comps_to_remove
        ]

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
        part_id2node_ids = {}

        slave_nodes = self.nodes.copy()

        if use_graph:
            part_id2node_ids = self.get_part_id2node_ids_graph(slave_nodes)
        else:
            part_id2node_ids = self.get_part_id2node_ids(slave_nodes)

        # add the forces for each part
        for part_id, node_ids in part_id2node_ids.items():
            self.part_id2slave_node_ids[part_id] = node_ids

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
