import os
import time
from typing import Dict
from mpcforces_extractor.reader.modelreaders import FemFileReader
from mpcforces_extractor.reader.mpcforces_reader import MPCForcesReader
from mpcforces_extractor.datastructure.entities import Element
from mpcforces_extractor.datastructure.subcases import Subcase


class MPCForceExtractor:
    """
    This class is used to extract the forces from the MPC forces file
    and calculate the forces for each rigid element by property
    """

    def __init__(self, fem_file_path, mpc_file_path, output_folder: str):
        self.fem_file_path: str = fem_file_path
        self.mpc_file_path: str = mpc_file_path
        self.output_folder: str = output_folder
        self.reader: FemFileReader = None
        self.mpc_forces_reader = None
        self.part_id2connected_node_ids: Dict = {}
        self.subcases = []
        # reset the graph (very important)
        Element.reset_graph()

        # create output folder if it does not exist, otherwise delete the content
        if os.path.exists(output_folder):
            for file in os.listdir(output_folder):
                file_path = os.path.join(output_folder, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
        else:
            os.makedirs(output_folder, exist_ok=True)

    def get_mpc2subcase_id2forces(self, block_size: int) -> dict:
        """
        This method reads the FEM File and the MPCF file and extracts the forces
        in a dictory with the rigid element as the key and the property2forces dict as the value
        """
        self.mpc_forces_reader = MPCForcesReader(self.mpc_file_path)
        self.mpc_forces_reader.bulid_subcases()
        self.subcases = Subcase.subcases

        self.reader = FemFileReader(self.fem_file_path, block_size)
        print("Reading the FEM file")
        start_time = time.time()
        self.reader.create_entities()

        print("..took ", round(time.time() - start_time, 2), "seconds")
        print("Building the mpcs")
        start_time = time.time()
        self.reader.get_rigid_elements()
        print("..took ", round(time.time() - start_time, 2), "seconds")

        self.reader.get_loads()

        mpc2subcase_id2forces = {}

        # Get the connected Nodes for all nodes
        self.part_id2connected_node_ids = Element.get_part_id2node_ids_graph()

        for mpc in self.reader.rigid_elements:

            part_id2slaveNodes = mpc.get_slave_nodes_intersection(
                self.part_id2connected_node_ids
            )

            for subcase in Subcase.subcases:
                part_id2forces = subcase.get_part_id2sum_forces(part_id2slaveNodes)
                if mpc not in mpc2subcase_id2forces:
                    mpc2subcase_id2forces[mpc] = {}
                mpc2subcase_id2forces[mpc][subcase.subcase_id] = part_id2forces

        return mpc2subcase_id2forces
