from typing import Dict, List


class MPC:
    """
    This class is a Multiple Point Constraint (MPC) class that is used to store the nodes and the dofs
    """

    def __init__(self, element_id: int, master_node2coords, nodes: List, dofs: str):
        self.element_id: int = element_id
        if master_node2coords is not None:
            self.master_node: Dict = master_node2coords
        else:
            self.master_node: Dict = {}
            print("master_node2coords is None for element_id", element_id)
        self.nodes: List = nodes
        self.dofs: int = dofs
        self.property2nodes: Dict = {}

    def sum_forces_by_property(self, node2force: Dict):
        """
        This method is used to sum the forces by property
        """
        forces = {}
        for property_id, nodes in self.property2nodes.items():
            forces[property_id] = [0, 0, 0, 0, 0, 0]
            for node in nodes:

                if node not in node2force:
                    print(
                        f"Node {node} not found in the MPC forces file - bug or zero - you decide!"
                    )
                    continue

                force = node2force[node]
                force_x = force[0]
                force_y = force[1]
                force_z = force[2]
                moment_x = force[3]
                moment_y = force[4]
                moment_z = force[5]

                forces[property_id][0] += force_x
                forces[property_id][1] += force_y
                forces[property_id][2] += force_z
                forces[property_id][3] += moment_x
                forces[property_id][4] += moment_y
                forces[property_id][5] += moment_z

        # {1:[500, 0 0 ], 2:[-500, 0, 0]}
        return forces

    def sort_nodes_by_property(self, node2property: Dict):
        """
        This method is used to sort the nodes by property
        """
        for node in self.nodes:
            property_id = node2property[node]
            if property_id not in self.property2nodes:
                self.property2nodes[property_id] = []

            if node not in self.property2nodes[property_id]:
                self.property2nodes[property_id].append(node)
