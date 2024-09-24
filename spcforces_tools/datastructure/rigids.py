from typing import Dict, List
from enum import Enum
from spcforces_tools.datastructure.entities import Node


class MPC_CONFIG(Enum):
    """
    Enum to represent the MPC configuration
    """

    RBE2 = 1
    RBE3 = 2


class MPC:
    """
    This class is a Multiple Point Constraint (MPC) class that is used to store the nodes and the dofs
    """

    def __init__(
        self,
        *,
        element_id: int,
        mpc_config: MPC_CONFIG,
        master_node: Node,
        nodes: List,
        dofs: str,
    ):
        self.element_id: int = element_id
        self.mpc_config: MPC_CONFIG = mpc_config
        if master_node is None:
            print("Master_node2coords is None for element_id", element_id)
        self.master_node = master_node
        self.nodes: List = nodes
        self.dofs: int = dofs
        self.part_id2force = {}
        self.part_id2node_ids = {}

    def sum_forces_by_connected_parts(
        self, node_id2force: Dict, part_id2connected_node_ids: Dict
    ) -> Dict:
        """
        This method is used to sum the forces by connected - parts NEW
        """
        forces = {}

        self.part_id2node_ids = self.__get_slave_nodes_intersection(
            part_id2connected_node_ids
        )

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

    def __get_slave_nodes_intersection(self, part_id2connected_node_ids: Dict) -> Dict:
        """
        This method is used to get the slave nodes intersection
        """
        part_id2node_ids = {}
        slave_node_ids = [node.id for node in self.nodes]
        for part_id, node_ids in part_id2connected_node_ids.items():
            part_id2node_ids[part_id] = list(set(node_ids).intersection(slave_node_ids))
        return part_id2node_ids
