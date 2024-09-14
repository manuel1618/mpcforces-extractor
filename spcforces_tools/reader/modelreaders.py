from typing import List
import re
from spcforces_tools.datastructure.rigids import MPC, RBE2


class FemFileReader:
    """
    This class is used to read the .fem file and extract the nodes and the rigid elements
    """

    element_keywords2number_nodes: List = {"CTRIA3": 3, "CQUAD4": 4}

    file_path: str = None
    file_content: str = None
    nodes: List = []
    rigid_elements: List[MPC] = []
    node2property = {}

    def __init__(self, file_path):
        self.file_path = file_path
        self.nodes = []
        self.rigid_elements = []
        self.node2property = {}
        self.__read_lines()

    def __read_lines(self):
        """
        This method reads the lines of the .fem file
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            self.file_content = file.readlines()

    def get_nodes(self):
        """
        This method is used to extract the nodes from the .fem file
        """
        for line in self.file_content:
            if line.startswith("GRID"):
                line = re.sub(r"\s+", ";", line).split(";")
                node_id = line.split(";")[1]
                self.nodes.append(node_id)

    def bulid_node2property(self):
        """
        This method is used to build the node2property dictionary.
        Its the main info needed for getting the forces by property
        """
        for line in self.file_content:
            for _, element_keyword in enumerate(self.element_keywords2number_nodes):
                if line.startswith(element_keyword):
                    line_content = re.sub(r"\s+", ";", line).split(";")
                    property_id = line_content[2]
                    nodes = line_content[3:]
                    for node in nodes:
                        if node not in self.node2property:
                            self.node2property[node] = property_id

    def get_rigid_elements(self):
        """
        This method is used to extract the rigid elements from the .fem file
        Currently: only RBE2 is supported TODO: add support for RBE3
        """

        for i, _ in enumerate(self.file_content):
            line = self.file_content[i]
            if line.startswith("RBE2"):
                line = re.sub(r"\s+", ";", line).split(";")
                element_id = line[1]
                dofs = line[3]
                nodes = line[4:]
                line2 = self.file_content[i + 1]
                while line2.startswith("+"):
                    line2 = re.sub(r"\s+", ";", line2).split(";")
                    nodes += line2[1:]
                    i += 1
                    line2 = self.file_content[i]

                # remove anything with a . in nodes, those are the weights
                nodes = [node for node in nodes if "." not in node and node != ""]

                self.rigid_elements.append(RBE2(element_id, nodes, dofs))
