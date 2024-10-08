from typing import Dict, List
from enum import Enum
from mpcforces_extractor.datastructure.entities import Node


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

    def get_slave_nodes_intersection(self, part_id2connected_node_ids: Dict) -> Dict:
        """
        This method is used to get the slave nodes intersection
        """
        part_id2node_ids = {}
        slave_node_ids = [node.id for node in self.nodes]
        for part_id, node_ids in part_id2connected_node_ids.items():
            part_id2node_ids[part_id] = list(set(node_ids).intersection(slave_node_ids))

        self.part_id2node_ids = part_id2node_ids
        return part_id2node_ids
