import os
import time
from typing import Optional
from mpcforces_extractor.reader.modelreaders import FemFileReader
from mpcforces_extractor.reader.forces_reader import ForcesReader
from mpcforces_extractor.datastructure.subcases import Subcase, ForceType


class MPCForceExtractor:
    """
    This class is used to extract the forces from the MPC forces file
    and calculate the forces for each rigid element by property
    """

    def __init__(
        self, fem_file_path, mpcf_file_path, output_folder: Optional[str] = None
    ):
        self.fem_file_path: str = fem_file_path
        self.mpcf_file_path: str = mpcf_file_path
        self.output_folder: str = output_folder
        self.reader: FemFileReader = None
        self.mpc_forces_reader = None
        self.subcases = []

        if output_folder:
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
        if self.__mpcf_file_exists():
            self.mpc_forces_reader = ForcesReader(self.mpcf_file_path)
            self.mpc_forces_reader.build_subcases(force_type=ForceType.MPCFORCE)
            self.subcases = Subcase.subcases

        # Think about removing it from here to another class
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

    def __mpcf_file_exists(self) -> bool:
        """
        This method checks if the MPC forces file exists
        """
        return os.path.exists(self.mpcf_file_path) and os.path.isfile(
            self.mpcf_file_path
        )


class SPCForcesExtractor:
    """
    This class is used to extract the forces from the SPC forces file
    and calculate the forces for each rigid element by property
    """

    def __init__(self, fem_file_path: str, spcf_file_path: str) -> None:
        self.fem_file_path: str = fem_file_path
        self.spcf_file_path: str = spcf_file_path
        self.reader: FemFileReader = None
        self.spc_forces_reader = None
        self.subcases = []

    def build_fem_and_subcase_data(self, block_size: int) -> None:
        """
        This method reads the FEM File and the SPCF file and extracts the forces
        """
        if self.__spcf_file_exists():
            self.spc_forces_reader = ForcesReader(self.spcf_file_path)
            self.spc_forces_reader.build_subcases(force_type=ForceType.SPCFORCE)
            self.subcases = Subcase.subcases

        # Think about removing it from here to another class
        self.reader = FemFileReader(self.fem_file_path, block_size)
        print("Reading the FEM file")
        start_time = time.time()
        self.reader.create_entities()
        print("..took ", round(time.time() - start_time, 2), "seconds")

    def __spcf_file_exists(self) -> bool:
        """
        This method checks if the SPC forces file exists
        """
        return os.path.exists(self.spcf_file_path) and os.path.isfile(
            self.spcf_file_path
        )
