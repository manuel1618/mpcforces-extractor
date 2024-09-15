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
    blocksize: int = None

    def __init__(self, file_path, block_size: int):
        self.file_path = file_path
        self.nodes = []
        self.rigid_elements = []
        self.node2property = {}
        self.__read_lines()
        self.blocksize = block_size

    def __read_lines(self):
        """
        This method reads the lines of the .fem file
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            self.file_content = file.readlines()

    def split_line(self, line: str) -> List:
        """
        This method is used to split a line into blocks of blocksize, and
        remove the newline character and strip the content of the block
        """
        line_content = [
            line[j : j + self.blocksize] for j in range(0, len(line), self.blocksize)
        ]

        if "\n" in line_content:
            line_content.remove("\n")

        return  # TODO
        line_content = [line.strip() for line in line_content]
        return line_content

    def bulid_node2property(self):
        """
        This method is used to build the node2property dictionary.
        Its the main info needed for getting the forces by property
        """
        for line in self.file_content:
            for _, element_keyword in enumerate(self.element_keywords2number_nodes):
                if line.startswith(element_keyword):
                    line_content = self.split_line(line)
                    property_id = int(line_content[2].strip())
                    nodes = [node.strip() for node in line_content[3:]]

                    for node in nodes:
                        if node not in self.node2property:
                            self.node2property[node] = property_id

    def get_rigid_elements(self):
        """
        This method is used to extract the rigid elements from the .fem file
        Currently: only RBE2 is supported TODO: add support for RBE3
        """

        element_keywords = ["RBE2", "RBE3"]

        for i, _ in enumerate(self.file_content):
            line = self.file_content[i]

            if line.split(" ")[0] not in element_keywords:
                continue

            line_content = self.split_line(line)
            element_id: int = int(line_content[1])
            dofs: int = None
            nodes: List = []
            if line.startswith("RBE3"):
                dofs = int(line_content[4])
                nodes = line_content[7:]

            elif line.startswith("RBE2"):
                dofs = int(line_content[3])
                nodes = [node.strip() for node in line_content[4:]]

            line2 = self.file_content[i + 1]
            while line2.startswith("+"):
                line_content = self.split_line(line2)
                for j, _ in enumerate(line_content):
                    if j == 0:
                        continue
                    if "." in line_content[j]:
                        j += 1
                        continue
                    nodes.append(line_content[j])

                i += 1
                line2 = self.file_content[i]

            # remove anything with a . in nodes, those are the weights
            nodes = [node for node in nodes if "." not in node and node != ""]

            self.rigid_elements.append(MPC(element_id, nodes, dofs))
