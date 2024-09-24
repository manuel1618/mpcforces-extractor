from typing import List, Dict
from spcforces_tools.datastructure.rigids import MPC, MPC_CONFIG
from spcforces_tools.datastructure.entities import Element1D, Element, Node
from spcforces_tools.datastructure.forces import Force


class FemFileReader:
    """
    This class is used to read the .fem file and extract the nodes and the rigid elements
    """

    element_keywords: List = [
        "CTRIA3",
        "CQUAD4",
        "CTRIA6",
        "CQUAD8",
        "CHEXA",
        "CPENTA",
        "CTETRA",
        "CROD",
        "CTUBE",
        "CBEAM",
        "CBAR",
    ]

    file_path: str = None
    file_content: str = None
    nodes_id2node: Dict = {}
    rigid_elements: List[MPC] = []
    node2property = {}
    force_id2force: Dict = {}
    blocksize: int = None

    def __init__(self, file_path, block_size: int):
        self.file_path = file_path
        self.blocksize = block_size
        self.nodes_id2node = {}
        self.rigid_elements = []
        self.node2property = {}
        self.file_content = self.__read_lines()
        self.__read_nodes()
        self.elements_1D = []
        self.elements_3D = []

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
                node = Node(node_id, [x, y, z])
                self.nodes_id2node[node.id] = node

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

            line_content = self.split_line(line)
            if len(line_content) < 2:
                continue
            element_keyword = line_content[0]

            if element_keyword not in self.element_keywords:
                continue

            line_content = self.split_line(line)
            property_id = int(line_content[2])

            if element_keyword in ["CBEAM", "CBAR", "CTUBE", "CROD"]:
                element = Element1D(
                    int(line_content[1]),
                    property_id,
                    int(line_content[3]),
                    int(line_content[4]),
                )
                self.elements_1D.append(element)
                node_ids = line_content[3:5]
                nodes = [self.nodes_id2node[int(node_id)] for node_id in node_ids]

            else:
                node_ids = line_content[3:]

                if i < len(self.file_content) - 1:
                    line2 = self.file_content[i + 1]
                    while line2.startswith("+"):
                        line_content = self.split_line(line2)
                        node_ids += self.split_line(line2)[1:]
                        i += 1
                        line2 = self.file_content[i]

                nodes = [self.nodes_id2node[int(node_id)] for node_id in node_ids]
                self.elements_3D.append(
                    Element(int(line_content[1]), property_id, nodes)
                )

            for node in node_ids:
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
            node_ids: List = []
            master_node = None
            mpc_config = None

            if line.startswith("RBE3"):
                mpc_config = MPC_CONFIG.RBE3
                master_node_id = int(line_content[3])
                master_node = self.nodes_id2node[master_node_id]
                dofs = int(line_content[4])
                node_ids = line_content[7:]

            elif line.startswith("RBE2"):
                mpc_config = MPC_CONFIG.RBE2
                master_node_id = int(line_content[2])
                master_node = self.nodes_id2node[master_node_id]
                dofs = int(line_content[3])
                node_ids = line_content[4:]
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
                        node_ids.append(line_content[j])

                    i += 1
                    if i == len(self.file_content) - 1:
                        break
                    line2 = self.file_content[i]

            # remove anything with a . in nodes, those are the weights
            node_ids = [
                int(node) for node in node_ids if "." not in node and node != ""
            ]
            # cast to int
            nodes = [self.nodes_id2node[id] for id in node_ids]
            self.rigid_elements.append(
                MPC(element_id, mpc_config, master_node, nodes, dofs)
            )

    def get_forces(self):
        """
        This method is used to extract the forces from the .fem file
        """
        for i, _ in enumerate(self.file_content):
            line = self.file_content[i]

            if line.startswith("FORCE"):
                line_content = self.split_line(line)
                force_id = int(line_content[1])
                node_id = int(line_content[2])
                system_id = int(line_content[3])
                scale_factor = float(line_content[4])
                components = line_content[5:8]
                FemFileReader.force_id2force[force_id] = Force(
                    force_id, node_id, system_id, scale_factor, components
                )
