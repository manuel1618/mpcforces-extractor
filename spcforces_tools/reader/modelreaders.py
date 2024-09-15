from typing import List
from spcforces_tools.datastructure.rigids import MPC


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

    def __get_nodes(self, blocksize: int):
        """
        This method is used to extract the nodes from the .fem file
        """
        for line in self.file_content:
            if line.startswith("GRID"):
                line_content = [
                    line[j : j + blocksize] for j in range(0, len(line), blocksize)
                ]
                node_id = line_content[1]
                self.nodes.append(node_id)

    def bulid_node2property(self, blocksize: int):
        """
        This method is used to build the node2property dictionary.
        Its the main info needed for getting the forces by property
        """
        for line in self.file_content:
            for _, element_keyword in enumerate(self.element_keywords2number_nodes):
                if line.startswith(element_keyword):
                    line_content = [
                        line[j : j + blocksize] for j in range(0, len(line), blocksize)
                    ]
                    property_id = int(line_content[2].strip())
                    nodes = [node.strip() for node in line_content[3:]]

                    for node in nodes:
                        if node not in self.node2property:
                            self.node2property[node] = property_id

    def get_rigid_elements(self, blocksize: int):
        """
        This method is used to extract the rigid elements from the .fem file
        Currently: only RBE2 is supported TODO: add support for RBE3
        """

        for i, _ in enumerate(self.file_content):
            line = self.file_content[i]
            if line.startswith("RBE2"):
                i = self.read_rbe2(blocksize, line, i)
            elif line.startswith("RBE3"):
                i = self.read_rbe3(blocksize, line, i)

    def read_rbe3(self, blocksize: int, line: str, line_number: int) -> int:
        """
        Reads in an RBE3 Element with blockdata
        """
        line_content = [line[j : j + blocksize] for j in range(0, len(line), blocksize)]

        element_id = int(line_content[1].strip())
        dofs = int(line_content[4].strip())
        nodes = [node.strip() for node in line_content[7:]]

        line2 = self.file_content[line_number + 1]
        while line2.startswith("+"):
            line_content = [
                line2[j : j + blocksize] for j in range(0, len(line2), blocksize)
            ]
            line_content.remove("\n") if "\n" in line_content else None

            for j, _ in enumerate(line_content):
                if j == 0:
                    continue
                if "." in line_content[j]:
                    j += 1
                    continue
                nodes.append(line_content[j].strip())

            line_number += 1
            line2 = self.file_content[line_number]

        # remove anything with a . in nodes, those are the weights
        nodes = [node for node in nodes if "." not in node and node != ""]

        self.rigid_elements.append(MPC(element_id, nodes, dofs))
        return line_number

    def read_rbe2(self, blocksize: int, line: str, line_number: int) -> int:
        """
        Reads in an RBE2 Element with blockdata
        """
        line_content = [line[j : j + blocksize] for j in range(0, len(line), blocksize)]
        line_content.remove("\n") if "\n" in line_content else None

        element_id = int(line_content[1].strip())
        dofs = int(line_content[3].strip())
        nodes = [node.strip() for node in line_content[4:]]

        line2 = self.file_content[line_number + 1]
        while line2.startswith("+"):
            line_content = [
                line2[j : j + blocksize] for j in range(0, len(line2), blocksize)
            ]
            nodes += [node.strip() for node in line_content[1:]]
            line_number += 1
            line2 = self.file_content[line_number]

        # remove anything with a . in nodes, those are the weights
        nodes = [node for node in nodes if "." not in node and node != ""]

        self.rigid_elements.append(MPC(element_id, nodes, dofs))
        return line_number
