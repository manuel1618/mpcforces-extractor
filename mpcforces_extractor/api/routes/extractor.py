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


router = APIRouter()


@router.post("/run-extractor")
async def run_extractor(request: Request, file_request: RunExtractorRequest):
    """
    Run the extractor. This is the main endpoint to run the program
    """
    fem_file = file_request.fem_filename
    model_name = fem_file.split(".")[0]
    mpcf_file = file_request.mpcf_filename
    spcf_file = file_request.spcf_filename

    print(f"Running extractor with files: {fem_file}, {mpcf_file}, {spcf_file}")

    # Clear all Instances
    Node.reset()
    Element1D.reset()
    Element.reset_graph()
    Subcase.reset()
    MPC.reset()
    SPCCluster.reset()
    SPC.reset()

    total_start_time = time.time()

    block_size = 8
    model_output_folder = str(OUTPUT_FOLDER) + os.sep + f"{fem_file.split('.')[0]}"
    fem_file_path = str(UPLOAD_FOLDER) + os.sep + fem_file
    mpcf_file_path = str(UPLOAD_FOLDER) + os.sep + mpcf_file
    spcf_file_path = str(UPLOAD_FOLDER) + os.sep + spcf_file

    fem_file_extracter = FEMExtractor(fem_file_path, block_size)
    fem_file_extracter.build_fem_data()

    if os.path.exists(mpcf_file_path):
        mpc_force_extractor = MPCForceExtractor(mpcf_file_path)
        mpc_force_extractor.build_subcase_data()

    if os.path.exists(spcf_file_path):
        spc_forces_extractor = SPCForcesExtractor(spcf_file_path)
        spc_forces_extractor.build_subcase_data()
        SPCCluster.build_spc_cluster()
        SPCCluster.calculate_force_sum()

    app = request.app
    app.db = Database(model_output_folder + f"/{model_name}.db")
    app.db.populate_database()

    total_end_time = time.time()
    total_time = total_end_time - total_start_time
    total_time_mins = total_time / 60.0
    print("---------------------------------")
    print(
        f"Total time taken: {round(total_time,2)} s (= {round(total_time_mins,2)} mins)"
    )

    # Implement your logic here to run the extractor using the provided filenames
    # For example, call your main routine here
    try:
        # Assuming you have a function called run_extractor_function
        # run_extractor_function(fem_file, mpcf_file)
        return {"message": "Extractor run successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
