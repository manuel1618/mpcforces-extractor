import os
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
from mpcforces_extractor.api.db.database import MPCDatabase


router = APIRouter()


@router.post("/run-extractor")
async def run_extractor(request: Request, file_request: RunExtractorRequest):
    """
    Run the extractor. This is the main endpoint to run the program
    """
    fem_file = file_request.fem_filename
    mpcf_file = file_request.mpcf_filename

    print(f"Running extractor with files: {fem_file}, {mpcf_file}")

    # Clear all Instances
    Node.reset()
    Element1D.reset()
    Element.reset_graph()
    Subcase.reset()
    MPC.reset()

    blocksize = 8
    model_output_folder = str(OUTPUT_FOLDER) + os.sep + f"{fem_file.split('.')[0]}"

    fem_file_extracter = FEMExtractor(
        fem_file_path=str(UPLOAD_FOLDER) + os.sep + fem_file, block_size=blocksize
    )
    fem_file_extracter.extract_fem_data()

    mpc_force_extractor = MPCForceExtractor(mpcf_file)

    spc_forces_extractor = SPCForcesExtractor(
        str(UPLOAD_FOLDER) + os.sep + mpcf_file,
    )

    spc_forces_extractor.build_subcase_data()
    mpc_force_extractor.build_subcase_data()
    app = request.app
    app.db = MPCDatabase(model_output_folder + "/db.db")
    app.db.populate_database()

    # Implement your logic here to run the extractor using the provided filenames
    # For example, call your main routine here
    try:
        # Assuming you have a function called run_extractor_function
        # run_extractor_function(fem_file, mpcf_file)
        return {"message": "Extractor run successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
