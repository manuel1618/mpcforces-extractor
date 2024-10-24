from typing import List


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
        self.node_id2forces = {}
        Subcase.subcases.append(self)

    def add_force(self, node_id: int, forces: List) -> None:
        """
        This method is used to add the forces for a node
        """
        self.node_id2forces[node_id] = forces

    def get_sum_forces(self, node_ids: List) -> None:
        """
        This method is used to sum the forces for all nodes
        """
        sum_forces = [0, 0, 0, 0, 0, 0]
        for node_id in node_ids:
            forces = self.node_id2forces[node_id]
            sum_forces = [sf + f for sf, f in zip(sum_forces, forces)]
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
