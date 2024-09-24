from typing import List


class Force:
    """
    Simple representation of a force from the .fem file
    """

    id: int
    node_id: int
    system_id: int
    compenents: List[float]

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
