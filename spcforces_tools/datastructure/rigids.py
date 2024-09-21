from typing import Dict, List
from spcforces_tools.datastructure.entities import Node


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

    def sum_forces_by_connected_parts(self, node_id2force: Dict):
        """
        This method is used to sum the forces by connected - parts NEW
        """
        forces = {}
        part_id2node_ids = {}

        # get the connected nodes for each part (attached elements)
        node_stack = self.nodes.copy()
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
