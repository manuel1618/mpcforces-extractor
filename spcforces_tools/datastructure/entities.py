from typing import List


class Element1D:
    """
    This class represents the 1D elements
    """

    id: int
    property_id: int
    node1: int
    node2: int
    all_elements = []

    def __init__(self, element_id: int, property_id: int, node1: int, node2: int):
        self.id = element_id
        self.property_id = property_id
        self.node1 = node1
        self.node2 = node2
        Element1D.all_elements.append(self)


class Element:
    """
    This class is used to store the 2D/3D elements
    """

    id: int
    property_id: int
    nodes: list = []
    all_elements = []

    def __init__(self, element_id: int, property_id: int, nodes: list):
        self.id = element_id
        self.property_id = property_id
        self.nodes = nodes
        Element.all_elements.append(self)


class Node:
    """
    This class is used to store the nodes
    """

    id: int
    coords: List = []
    all_nodes: List = []

    def __init__(self, node_id: int, coords: List):
        self.id = node_id
        self.coords = coords
        Node.all_nodes.append(self)
