import time
from typing import List, Dict
import networkx as nx


class Node:
    """
    This class is used to store the nodes
    """

    node_id2node: Dict = {}

    def __init__(self, node_id: int, coords: List):
        self.id = node_id
        self.coords = coords
        Node.node_id2node[node_id] = self
        self.connected_elements = []

    def add_element(self, element):
        """
        This method adds the element to the connected elements
        """
        if element not in self.connected_elements:
            self.connected_elements.append(element)

    @staticmethod
    def reset() -> None:
        """
        This method resets the node_id2node dictionary
        """
        Node.node_id2node = {}


class Element1D:
    """
    This class represents the 1D elements
    """

    all_elements = []

    def __init__(self, element_id: int, property_id: int, node1: Node, node2: Node):
        self.id = element_id
        self.property_id = property_id
        self.node1 = node1
        self.node2 = node2
        Element1D.all_elements.append(self)

    @staticmethod
    def reset():
        """
        This method resets the all_elements list
        """
        Element1D.all_elements = []


class Element:
    """
    This class is used to store the 2D/3D elements
    """

    element_id2element: Dict = {}
    graph = nx.Graph()
    part_id2node_ids = {}

    @staticmethod
    def reset_graph():
        """
        This method is used to reset the graph (very important for testing)
        """
        Element.graph = nx.Graph()
        Element.element_id2element = {}
        Element.part_id2node_ids = {}

    def __init__(self, element_id: int, property_id: int, nodes: list):
        self.id = element_id
        self.property_id = property_id
        self.nodes = nodes
        for node in nodes:
            node.add_element(self)

        # Graph - careful: Careless implementation regarding nodes:
        # every node is connected to every other node.
        # Real implementation should be done depending on element keyword
        for node in nodes:
            for node2 in nodes:
                if node.id != node2.id:
                    # add the edge to the graph if it does not exist
                    if not Element.graph.has_edge(node, node2):
                        Element.graph.add_edge(node, node2)

        self.centroid = self.__calculate_centroid()
        self.neighbors = []
        self.element_id2element[self.id] = self
        Element.part_id2node_ids = {}

    def __calculate_centroid(self):
        """
        This method calculates the centroid of the element
        """
        centroid = [0, 0, 0]
        for node in self.nodes:
            for i in range(3):
                centroid[i] += node.coords[i]
        for i in range(3):
            centroid[i] /= len(self.nodes)
        return centroid

    @staticmethod
    def get_part_id2node_ids_graph(force_update: bool = False) -> Dict:
        """
        This method is used to get the part_id2node_ids using the graph
        """
        if force_update or not Part.part_id2node_ids:
            start_time = time.time()
            print("Building the part_id2node_ids using the graph")

            print("...Calculating connected components")
            connected_components = list(nx.connected_components(Element.graph.copy()))

            print(
                "Finished calculating the connected components, returning part_id2node_ids"
            )
            print("..took ", round(time.time() - start_time, 2), "seconds")

            for _, connected_component in enumerate(connected_components):
                Part(connected_component)

            return Part.part_id2node_ids
        return Part.part_id2node_ids


class Part:
    """
    This class ressembles a part in the model
    A part has a collection of connected nodes
    """

    total_parts = 0
    part_id2node_ids = {}

    def __init__(self, nodes: List[Node]):
        self.id = Part.total_parts + 1
        Part.total_parts += 1
        self.node_id2Node = {}
        for node in nodes:
            self.node_id2Node[node.id] = node
        self.part_id2node_ids[self.id] = [node.id for node in nodes]

    @staticmethod
    def reset():
        """
        This method resets all parts
        """
        Part.total_parts = 0
        Part.part_id2node_ids = {}
