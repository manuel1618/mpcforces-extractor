class Subcase:
    """
    This class is used to store the subcase information
    The purpose of this class is to make multiple subcases available
    in the mpcforces_extractor
    """

    subcase_id = 0
    time = 0
    node_id2forces = {}
    subcases = []

    def __init__(self, subcase_id, time):
        """
        Constructor
        """
        self.subcase_id = subcase_id
        self.time = time
        self.node_id2forces = {}
        self.part_id2sum_forces = {}
        Subcase.subcases.append(self)

    def add_force(self, node_id, forces):
        """
        This method is used to add the forces for a node
        """
        self.node_id2forces[node_id] = forces

    def add_part_id2sum_forces(self, part_id2connected_node_ids) -> None:
        """
        This method is used to sum the forces for all nodes
        """
        for part_id, part_node_ids in part_id2connected_node_ids.items():
            sum_forces = [0, 0, 0, 0, 0, 0]
            for node_id in part_node_ids:
                forces = self.node_id2forces[node_id]
                for i, _ in enumerate(forces):
                    sum_forces[i] += forces[i]
            self.part_id2sum_forces[part_id] = sum_forces

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
