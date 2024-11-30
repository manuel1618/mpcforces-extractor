from typing import Dict, List
from enum import Enum
from mpcforces_extractor.datastructure.entities import Node, Element
from mpcforces_extractor.datastructure.subcases import Subcase, ForceType


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

    config_2_id_2_instance: Dict[int, "MPC"] = {}

    def __init__(
        self,
        *,  # fixes the too many positional arguments error from the linter by forcing the use of keyword arguments
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
        self.part_id2node_ids = {}

        # config_2_id_2_instance
        if mpc_config.value not in MPC.config_2_id_2_instance:
            MPC.config_2_id_2_instance[mpc_config.value] = {}

        if element_id in MPC.config_2_id_2_instance[mpc_config.value]:
            print("MPC element_id already exists", element_id)
        MPC.config_2_id_2_instance[mpc_config.value][element_id] = self

    @staticmethod
    def reset():
        """
        This method is used to reset the instances
        """
        MPC.config_2_id_2_instance = {}

    def get_part_id2force(self, subcase: Subcase) -> Dict:
        """
        This method is used to get the forces for each part of the MPC (connected slave nodes)
        """

        if not self.part_id2node_ids:
            # Connected groups of nodes - get then the intersection with the slave nodes
            part_id2connected_node_ids = Element.get_part_id2node_ids_graph()
            part_id2node_ids = {}
            mpc_node_ids = [node.id for node in self.nodes]
            mpc_node_ids.append(self.master_node.id)
            for part_id, node_ids in part_id2connected_node_ids.items():
                part_id2node_ids[part_id] = list(
                    set(node_ids).intersection(mpc_node_ids)
                )

            self.part_id2node_ids = part_id2node_ids

        # Calculate the summed forces for each part
        part_id2forces = {}
        for part_id, node_ids in self.part_id2node_ids.items():
            sum_forces = [0, 0, 0]
            if subcase is not None:
                sum_forces = subcase.get_sum_forces(node_ids, ForceType.MPCFORCE)
            part_id2forces[part_id] = sum_forces
        return part_id2forces

    def get_subcase_id2part_id2force(self) -> Dict:
        """
        This method is used to get the forces for each part of the MPC (connected slave nodes)
        """

        subcase_id2part_id2forces = {}
        for subcase in Subcase.subcases:
            part_id2forces = self.get_part_id2force(subcase)
            subcase_id2part_id2forces[subcase.subcase_id] = part_id2forces
        return subcase_id2part_id2forces
