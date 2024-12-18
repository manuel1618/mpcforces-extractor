import os
import time
from fastapi import APIRouter, HTTPException, Request
from mpcforces_extractor.api.db.schemas import RunExtractorRequest
from mpcforces_extractor.api.config import UPLOAD_FOLDER, OUTPUT_FOLDER
from mpcforces_extractor.force_extractor import (
    MPCForceExtractor,
    SPCForcesExtractor,
    FEMExtractor,
)
from mpcforces_extractor.datastructure.entities import Node, Element1D, Element
from mpcforces_extractor.datastructure.subcases import Subcase
from mpcforces_extractor.datastructure.rigids import MPC
from mpcforces_extractor.api.db.database import Database
from mpcforces_extractor.datastructure.loads import SPCCluster, SPC
from mpcforces_extractor.logging.logger import Logger

router = APIRouter()


@router.post("/run-extractor")
async def run_extractor(request: Request, file_request: RunExtractorRequest):
    """
    Run the extractor. This is the main endpoint to run the program
    """

    try:
        fem_file = file_request.fem_filename
        model_name = fem_file.split(".")[0]
        mpcf_file = file_request.mpcf_filename
        spcf_file = file_request.spcf_filename

        logger = Logger()
        logger.log_header("Running extractor")
        logger.log_info(f"FEM File: {fem_file}")
        logger.log_info(f"MPCF File: {mpcf_file}")
        logger.log_info(f"SPCF File: {spcf_file}")

        reset_instances()

        total_start_time = time.time()

        block_size = 8
        model_output_folder = str(OUTPUT_FOLDER) + os.sep + f"{fem_file.split('.')[0]}"
        fem_file_path = str(UPLOAD_FOLDER) + os.sep + fem_file
        mpcf_file_path = str(UPLOAD_FOLDER) + os.sep + mpcf_file
        spcf_file_path = str(UPLOAD_FOLDER) + os.sep + spcf_file

        logger.log_header("Reading FEM File")
        fem_file_extracter = FEMExtractor(fem_file_path, block_size)
        fem_file_extracter.build_fem_data()

        if os.path.exists(mpcf_file_path):
            logger.log_header("Reading MPCF File")
            mpc_force_extractor = MPCForceExtractor(mpcf_file_path)
            mpc_force_extractor.build_subcase_data()

        if os.path.exists(spcf_file_path):
            logger.log_header("Reading SPCF File")
            spc_forces_extractor = SPCForcesExtractor(spcf_file_path)
            spc_forces_extractor.build_subcase_data()
            logger.log_header("Building SPC Clusters")
            SPCCluster.build_spc_cluster()
            SPCCluster.calculate_force_sum()

        logger.log_header("Database Operations")
        logger.start_timing("Populating Database")
        app = request.app
        app.db = Database(model_output_folder + f"/{model_name}.db")
        app.db.populate_database()
        logger.stop_timing("Populating Database")

        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        total_time_mins = total_time / 60.0

        logger.log_header("Summary")
        logger.log_info(
            f"Total time taken: {round(total_time,2)} s (= {round(total_time_mins,2)} mins)"
        )

        logger.write_to_file(model_output_folder + f"/{model_name}_log.txt")

        return {"message": "Extractor run successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def reset_instances():
    """
    Reset the instances of the data structures
    """

    # Clear all Instances
    Node.reset()
    Element1D.reset()
    Element.reset_graph()
    Subcase.reset()
    MPC.reset()
    SPCCluster.reset()
    SPC.reset()
