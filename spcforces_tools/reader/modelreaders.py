from typing import List, Dict
from spcforces_tools.datastructure.rigids import MPC


class FemFileReader:
    """
    This class is used to read the .fem file and extract the nodes and the rigid elements
    """

    element_keywords2number_nodes: List = [
        "CTRIA3",
        "CQUAD4",
        "CTRIA6",
        "CQUAD8",
        "CHEXA",
        "CPENTA",
        "CTETRA",
    ]

    file_path: str = None
    file_content: str = None
    nodes2coords: Dict = {}
    rigid_elements: List[MPC] = []
    node2property = {}
    blocksize: int = None

    def __init__(self, file_path, block_size: int):
        self.file_path = file_path
        self.blocksize = block_size
        self.nodes = []
        self.rigid_elements = []
        self.node2property = {}
        self.file_content = self.__read_lines()
        self.__read_nodes()

    def __read_lines(self) -> List:
        """
        This method reads the lines of the .fem file
        """
        # check if the file exists
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return file.readlines()
        except FileNotFoundError:
            print(f"File {self.file_path} not found")
            return []

    def __read_nodes(self):
        """
        This method is used to read the nodes from the .fem file
        """
        for line in self.file_content:
            if line.startswith("GRID"):
                line_content = self.split_line(line)
                node_id = int(line_content[1])
                x = self.__node_coord_parser(line_content[3])
                y = self.__node_coord_parser(line_content[4])
                z = self.__node_coord_parser(line_content[5])
                self.nodes2coords[node_id] = [x, y, z]

    def __node_coord_parser(self, coord_str: str) -> float:
        """
        This method is used to parse the node coordinates
        """
        # Problem is the expenential notation without the E in it
        before_dot = coord_str.split(".")[0]
        after_dot = coord_str.split(".")[1]
        if "-" in after_dot:
            return float(before_dot + "." + after_dot.replace("-", "e-"))
        if "+" in after_dot:
            return float(before_dot + "." + after_dot.replace("+", "e+"))

        return float(coord_str)

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

        line_content = [line.strip() for line in line_content]
        return line_content

    def bulid_node2property(self):
        """
        This method is used to build the node2property dictionary.
        Its the main info needed for getting the forces by property
        """
        for i, _ in enumerate(self.file_content):
            line = self.file_content[i]
            for element_keyword in self.element_keywords2number_nodes:
                if line.startswith(element_keyword):
                    line_content = self.split_line(line)
                    property_id = int(line_content[2])
                    nodes = line_content[3:]

                    if i < len(self.file_content) - 1:
                        line2 = self.file_content[i + 1]
                        while line2.startswith("+"):
                            line_content = self.split_line(line2)
                            nodes += self.split_line(line2)[1:]
                            i += 1
                            line2 = self.file_content[i]

                    for node in nodes:
                        node = int(node)  # cast to int
                        if node not in self.node2property:
                            self.node2property[node] = property_id

    def get_rigid_elements(self):
        """
        This method is used to extract the rigid elements from the .fem file
        Currently: only RBE2 / RBE3 is supported
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
            master_node = None

            if line.startswith("RBE3"):
                master_node = int(line_content[3])
                dofs = int(line_content[4])
                nodes = line_content[7:]

            elif line.startswith("RBE2"):
                master_node = int(line_content[2])
                dofs = int(line_content[3])
                nodes = line_content[4:]

            master_coords = self.nodes2coords[master_node]
            if i < len(self.file_content) - 1:
                i += 1
                line2 = self.file_content[i]
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
                    if i == len(self.file_content) - 1:
                        break
                    line2 = self.file_content[i]

            # remove anything with a . in nodes, those are the weights
            nodes = [node for node in nodes if "." not in node and node != ""]
            # cast to int
            nodes = [int(node) for node in nodes]
            print(master_node, master_coords, nodes, dofs)
            self.rigid_elements.append(
                MPC(element_id, {master_node: master_coords}, nodes, dofs)
            )
