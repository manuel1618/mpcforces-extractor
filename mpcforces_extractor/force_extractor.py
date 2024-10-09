import os
import time
from mpcforces_extractor.reader.modelreaders import FemFileReader
from mpcforces_extractor.reader.mpcforces_reader import MPCForcesReader
from mpcforces_extractor.datastructure.entities import Element
from mpcforces_extractor.datastructure.rigids import MPC
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
        self.subcases = []
        # reset the graph (very important) and the MPCs
        Element.reset_graph()
        MPC.reset()

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

    def build_fem_and_subcase_data(self, block_size: int) -> None:
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
