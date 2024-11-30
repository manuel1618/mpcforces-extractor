from typing import List, Dict


class Moment:
    """
    Simple representation of a moment from the .fem file
    """

    def __init__(
        self,
        *,
        moment_id: int,
        node_id: int,
        system_id: int,
        scale_factor: float,
        compenents_from_file: List[str],
    ):
        self.id = moment_id
        self.node_id = node_id
        self.system_id = system_id
        self.compenents = [
            scale_factor * float(compenent) for compenent in compenents_from_file
        ]


class Force:
    """
    Simple representation of a force from the .fem file
    """

    def __init__(
        self,
        *,
        force_id: int,
        node_id: int,
        system_id: int,
        scale_factor: float,
        compenents_from_file: List[str],
    ):
        self.id = force_id
        self.node_id = node_id
        self.system_id = system_id
        self.compenents = [
            scale_factor * float(compenent) for compenent in compenents_from_file
        ]


class SPC:
    """
    Simple representation of a SPC from the .fem file (Single Point Constraint)
    """

    def __init__(
        self,
        node_id: int,
        system_id: int,
        dofs: Dict[int, float],
    ):
        self.node_id = node_id
        self.system_id = system_id
        self.dofs = dofs
        self.reaction_force = None

    def set_reaction_force(self, reaction_force: List[float]):
        """
        Set the reaction force
        """
        self.reaction_force = reaction_force


class SPCCluster:
    """
    A collection of SPCs
    """

    def __init__(self):
        self.spccs = []

    def add_spcc(self, spcc: SPC):
        """
        Add a SPC to the cluster
        """
        self.spccs.append(spcc)
