from typing import List
from enum import Enum


class ForceType(Enum):
    """
    Enum to differentiate between MPC and SPC forces
    """

    MPCFORCE = 1
    SPCFORCE = 2


class Subcase:
    """
    This class is used to store the subcase information
    The purpose of this class is to make multiple subcases available
    in the mpcforces_extractor
    """

    subcases = []

    def __init__(self, subcase_id: int, time: float):
        """
        Constructor
        """
        self.subcase_id = subcase_id
        self.time = time
        self.node_id2mpcforces = {}
        self.node_id2spcforces = {}
        Subcase.subcases.append(self)

    def add_force(self, node_id: int, forces: List, force_type: ForceType) -> None:
        """
        This method is used to add the forces for a node
        """
        if force_type == ForceType.MPCFORCE:
            self.node_id2mpcforces[node_id] = forces
        elif force_type == ForceType.SPCFORCE:
            self.node_id2spcforces[node_id] = forces

    def get_sum_forces(
        self,
        node_ids: List,
        force_type: ForceType,
    ) -> None:
        """
        This method is used to sum the forces for all nodes
        """
        forces = {}
        if force_type == ForceType.MPCFORCE:
            forces = self.node_id2mpcforces
        elif force_type == ForceType.SPCFORCE:
            forces = self.node_id2spcforces

        sum_forces = [0, 0, 0, 0, 0, 0]
        for node_id in node_ids:
            if node_id not in forces:
                print(f"Node {node_id} not found in mpcf, setting to 0.")
                continue
            force_vector = forces[node_id]
            sum_forces = [sf + f for sf, f in zip(sum_forces, force_vector)]
        return sum_forces

    @staticmethod
    def get_subcase_by_id(subcase_id: int):
        """
        This method is used to get a subcase by its id
        """
        for subcase in Subcase.subcases:
            if subcase.subcase_id == subcase_id:
                return subcase
        print(f"No Subcase with id {id} was found.")
        return None

    @staticmethod
    def reset():
        """
        This method is used to reset the subcases list
        """
        Subcase.subcases = []
