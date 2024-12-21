from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
from mpcforces_extractor.datastructure.rigids import MPC, MPC_CONFIG
from mpcforces_extractor.datastructure.entities import Element1D, Element, Node
from mpcforces_extractor.datastructure.loads import Moment, Force, SPC
from mpcforces_extractor.logging.logger import Logger
from mpcforces_extractor.reader.reader_utilities import modelReaderUtilities


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
    keyword_1d_elements = ["CROD", "CTUBE", "CBEAM", "CBAR"]
    keyword_loadcollectors = ["FORCE", "MOMENT", "SPC"]

    file_path: str = None
    file_content: str = None
    nodes_id2node: Dict = {}
    rigid_elements: List[MPC] = []
    load_id2load: Dict = {}
    node_id2spc: Dict = {}
    blocksize: int = None

    def __init__(self, file_path, block_size: int):
        self.file_path = file_path
        self.blocksize = block_size
        self.node_lines = []
        self.nodes_id2node = {}
        self.rigid_elements = []
        self.file_content = self.__read_lines()
        Logger().start_timing("Creating nodes")
        self.__read_nodes(True)
        Logger().stop_timing("Creating nodes")
        self.endGridLine = None
        self.endElementLine = None

    def __read_lines(self) -> List:
        """
        This method reads the lines of the .fem file
        """
        # check if the file exists
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return file.readlines()
        except FileNotFoundError:
            Logger().log_err(f"File {self.file_path} not found")
            return []

    def __identify_node_lines(self):
        """
        This method identifies the node lines in the file
        """
        grids_found = False
        for i, line in enumerate(self.file_content):
            if line.startswith("GRID"):
                grids_found = True
                self.node_lines.append(line)
            elif grids_found and not line.startswith("GRID"):
                self.endGridLine = i
                break

    def _process_node_chunk(self, chunk: List[str]) -> Dict[int, "Node"]:
        """
        Process a chunk of node lines to extract nodes.
        Returns a dictionary of node_id to Node.
        """
        nodes = {}
        for line in chunk:
            line_content = modelReaderUtilities.split_line(line, self.blocksize)
            node_id = int(line_content[1])
            coords = [
                modelReaderUtilities.node_coord_parser(line_content[j])
                for j in range(3, 6)
            ]
            node = Node(node_id, coords)
            self.nodes_id2node[node.id] = node
            nodes[node.id] = node
        return nodes

    def __read_nodes(self, parallel: bool = True):
        """
        This method processes the identified node lines using parallelization.
        """
        self.__identify_node_lines()

        if not self.node_lines:
            return

        if parallel:
            chunks = modelReaderUtilities.get_chunks(self.node_lines)
            with ThreadPoolExecutor() as executor:
                executor.map(self._process_node_chunk, chunks)
        else:
            self.__process_node_chunk(self.node_lines)

    def create_entities(self, parallel: bool = True):
        """
        Creates the Elements based on the .fem file
        """

        if parallel:
            chunks = modelReaderUtilities.get_chunks(
                self.file_content[self.endGridLine : self.endElementLine],
            )

            with ThreadPoolExecutor() as executor:
                futures = list(executor.map(self.process_element_chunk, chunks))

            element_1d_id_prop_node1_node2 = []
            element_3d_id_prop_nodes = []

            # After parallel processing, collect all the results
            for result in futures:
                element_1d_id_prop_node1_node2 += result[0]
                element_3d_id_prop_nodes += result[1]
        else:
            # Process all at once
            element_1d_id_prop_node1_node2, element_3d_id_prop_nodes = (
                self.process_element_chunk(
                    self.file_content[self.endGridLine : self.endElementLine]
                )
            )

        for element_id, property_id, node1, node2 in element_1d_id_prop_node1_node2:
            Element1D(element_id, property_id, node1, node2)

        for element_id, property_id, nodes in element_3d_id_prop_nodes:
            Element(element_id, property_id, nodes)

    def process_element_chunk(self, chunk: List[str]) -> List:
        """
        Processes a chunk of element lines to extract elements.
        Returns a list of tuples containing element_id, property_id, and nodes.
        """

        # for element creation
        element_1d_id_prop_node1_node2 = []
        element_3d_id_prop_nodes = []

        for i, line in enumerate(chunk):

            if not line.startswith(tuple(FemFileReader.element_keywords)):
                continue

            line_content = modelReaderUtilities.split_line(line, self.blocksize)
            if len(line_content) < 2:
                continue
            element_keyword = line_content[0]

            if element_keyword not in FemFileReader.element_keywords:
                continue

            if element_keyword in FemFileReader.keyword_loadcollectors:
                self.endElementLine = i - 1
                break

            property_id = int(line_content[2])
            nodes = []
            node_ids = []

            if element_keyword in FemFileReader.keyword_1d_elements:
                element_id = int(line_content[1])
                node1 = Node.node_id2node[int(line_content[3])]
                node2 = Node.node_id2node[int(line_content[4])]
                element_1d_id_prop_node1_node2.append(
                    (element_id, property_id, node1, node2)
                )
            else:
                node_ids = line_content[3:]
                element_id = int(line_content[1])

                # Initialize node_ids and continue appending lines until we reach a line that doesn't start with "+"
                while i + 1 < len(chunk) and chunk[i + 1].startswith("+"):
                    i += 1
                    # Append node IDs from the next continuation line (ignoring the '+')
                    node_ids += modelReaderUtilities.split_line(
                        chunk[i], self.blocksize
                    )[1:]

                node_ids = [
                    node_id.replace("+", "").strip()
                    for node_id in node_ids
                    if node_id.strip()
                ]

                nodes = [self.nodes_id2node[int(node_id)] for node_id in node_ids]
                element_3d_id_prop_nodes.append((element_id, property_id, nodes))

        return element_1d_id_prop_node1_node2, element_3d_id_prop_nodes

    def get_rigid_elements(self):
        """
        This method is used to extract the rigid elements from the .fem file
        Currently: only RBE2 / RBE3 is supported
        """

        element_keywords = ["RBE2", "RBE3"]

        for i, _ in enumerate(self.file_content[self.endGridLine :]):
            line = self.file_content[i]

            if line.split(" ")[0] not in element_keywords:
                continue

            line_content = modelReaderUtilities.split_line(line, self.blocksize)
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
                    line_content = modelReaderUtilities.split_line(
                        line2, self.blocksize
                    )
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
                MPC(
                    element_id=element_id,
                    mpc_config=mpc_config,
                    master_node=master_node,
                    nodes=nodes,
                    dofs=dofs,
                )
            )

    def get_loads(self):
        """
        This method is used to extract the loads from the .fem file (currently forces and moments)
        """
        for i, _ in enumerate(self.file_content[self.endElementLine :]):
            line = self.file_content[i]

            if line.startswith("FORCE"):
                line_content = modelReaderUtilities.split_line(line, self.blocksize)
                force_id = int(line_content[1])
                node_id = int(line_content[2])
                system_id = int(line_content[3])
                scale_factor = float(line_content[4])
                components_from_file = line_content[5:8]

                force = Force(
                    force_id=force_id,
                    node_id=node_id,
                    system_id=system_id,
                    scale_factor=scale_factor,
                    compenents_from_file=components_from_file,
                )
                FemFileReader.load_id2load[force_id] = force

            if line.startswith("MOMENT"):
                line_content = modelReaderUtilities.split_line(line, self.blocksize)
                moment_id = int(line_content[1])
                node_id = int(line_content[2])
                system_id = int(line_content[3])
                scale_factor = float(line_content[4])
                components_from_file = line_content[5:8]

                moment = Moment(
                    moment_id=moment_id,
                    node_id=node_id,
                    system_id=system_id,
                    scale_factor=scale_factor,
                    compenents_from_file=components_from_file,
                )
                FemFileReader.load_id2load[moment_id] = moment

    def get_spcs(self):
        """
        This method is used to extract the constraints (SPCs) from the .fem file
        """

        spc_id2system_id = {}
        spc_id_2dof_id2dof_value = {}

        for i, _ in enumerate(self.file_content[self.endElementLine :]):
            line = self.file_content[i]

            if not line.startswith("SPC"):
                continue

            line_content = modelReaderUtilities.split_line(line, self.blocksize)
            if len(line_content) < 2:
                continue

            if line_content[0].strip() == "SPC":
                line_content = modelReaderUtilities.split_line(line, self.blocksize)
                system_id = int(line_content[1])
                node_id = int(line_content[2])
                dof_ids = line_content[3]
                dof_value = float(line_content[4])

                if node_id not in spc_id2system_id:
                    spc_id2system_id[node_id] = system_id
                    spc_id_2dof_id2dof_value[node_id] = {}
                    if len(dof_ids) > 1:
                        for i, _ in enumerate(dof_ids):
                            spc_id_2dof_id2dof_value[node_id][
                                int(dof_ids[i])
                            ] = dof_value
                    else:
                        spc_id_2dof_id2dof_value[node_id][int(dof_ids)] = dof_value
                else:
                    Logger().log_warn(
                        "Duplicate SPC found, ignoring. Node id: ", node_id
                    )

        for node_id, system_id in spc_id2system_id.items():
            spc = SPC(node_id, system_id, spc_id_2dof_id2dof_value[node_id])
            self.node_id2spc[node_id] = spc
