import os
from mpcforces_extractor.reader.modelreaders import FemFileReader
from mpcforces_extractor.reader.forces_reader import ForcesReader
from mpcforces_extractor.datastructure.subcases import Subcase, ForceType
from mpcforces_extractor.logging.logger import Logger


class MPCForceExtractor:
    """
    This class is used to extract the forces from the MPC forces file
    and calculate the forces for each rigid element by property
    """

    def __init__(self, mpcf_file_path) -> None:
        self.mpcf_file_path: str = mpcf_file_path
        self.mpc_forces_reader = None
        self.subcases = []

    def build_subcase_data(self) -> None:
        """
        This method reads the FEM File and the MPCF file and extracts the forces
        in a dictory with the rigid element as the key and the property2forces dict as the value
        """
        if self.__mpcf_file_exists():
            self.mpc_forces_reader = ForcesReader(self.mpcf_file_path)
            self.mpc_forces_reader.build_subcases(force_type=ForceType.MPCFORCE)
            self.subcases = Subcase.subcases

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

    def __init__(self, spcf_file_path: str) -> None:
        self.spcf_file_path: str = spcf_file_path
        self.spc_forces_reader = None
        self.subcases = []

    def build_subcase_data(self) -> None:
        """
        This method reads the FEM File and the SPCF file and extracts the forces
        """
        if self.__spcf_file_exists():
            self.spc_forces_reader = ForcesReader(self.spcf_file_path)
            self.spc_forces_reader.build_subcases(force_type=ForceType.SPCFORCE)
            self.subcases = Subcase.subcases
        else:
            Logger().log_warn("SPC Forces file does not exist")

    def __spcf_file_exists(self) -> bool:
        """
        This method checks if the SPC forces file exists
        """
        return os.path.exists(self.spcf_file_path) and os.path.isfile(
            self.spcf_file_path
        )


class FEMExtractor:
    """ "
    This class is used to extract the data from the .fem file
    """

    def __init__(self, fem_file_path: str, block_size: int) -> None:
        self.fem_file_path: str = fem_file_path
        self.reader: FemFileReader = None
        self.block_size: int = block_size

    def build_fem_data(self):
        """
        Builds the main entities from the FEM file
        """
        logger = Logger()
        self.reader = FemFileReader(self.fem_file_path, self.block_size)
        logger.start_timing("Reading the FEM file")
        self.reader.create_entities()
        logger.stop_timing("Reading the FEM file")

        logger.start_timing("Building the rigid elements")
        self.reader.get_rigid_elements()
        logger.stop_timing("Building the rigid elements")

        logger.start_timing("Building the loads")
        self.reader.get_loads()
        logger.stop_timing("Building the loads")

        logger.start_timing("Building the constraints")
        self.reader.get_spcs()
        logger.stop_timing("Building the constraints")
