import os
from typing import List
from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Request,
    Query,
    Form,
    UploadFile,
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from mpcforces_extractor.api.db.database import (
    MPCDatabase,
    MPCDBModel,
    NodeDBModel,
    SubcaseDBModel,
)
from mpcforces_extractor.api.db.schemas import RunExtractorRequest, DatabaseRequest
from mpcforces_extractor.force_extractor import MPCForceExtractor
from mpcforces_extractor.datastructure.entities import Element, Node, Element1D
from mpcforces_extractor.datastructure.subcases import Subcase
from mpcforces_extractor.datastructure.rigids import MPC
from mpcforces_extractor.api.config import (
    ITEMS_PER_PAGE,
    UPLOAD_FOLDER,
    OUTPUT_FOLDER,
    STATIC_DIR,
    TEMPLATES_DIR,
)


# Setup Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app = FastAPI()

# Mount the static files directory
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


# API endpoint to get all MPCs
@app.get("/api/v1/mpcs", response_model=List[MPCDBModel])
async def get_mpcs() -> List[MPCDBModel]:
    """Get all MPCs"""
    if not hasattr(app, "db"):
        raise HTTPException(status_code=500, detail="Database not initialized")
    return await app.db.get_mpcs()


# API endpoint to get a specific MPC by ID
@app.get("/api/v1/mpcs/{mpc_id}", response_model=MPCDBModel)
async def get_mpc(mpc_id: int) -> MPCDBModel:
    """Get info about a specific MPC"""
    if not hasattr(app, "db"):
        raise HTTPException(status_code=500, detail="Database not initialized")
    mpc = await app.db.get_mpc(mpc_id)
    if mpc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MPC with id: {mpc_id} does not exist",
        )

    return mpc


# API endpoint to remove an MPC by ID
@app.delete("/api/v1/mpcs/{mpc_id}")
async def remove_mpc(mpc_id: int):
    """Remove an MPC"""
    if not hasattr(app, "db"):
        raise HTTPException(status_code=500, detail="Database not initialized")

    await app.db.remove_mpc(mpc_id)
    return {"message": f"MPC with id: {mpc_id} removed"}


@app.get("/api/v1/nodes", response_model=List[NodeDBModel])
async def get_nodes(page: int = Query(1, ge=1)) -> List[NodeDBModel]:
    """
    Get nodes with pagination (fixed 100 items per page)
    """

    if not hasattr(app, "db"):
        raise HTTPException(status_code=500, detail="Database not initialized")

    # Calculate offset based on the current page
    offset = (page - 1) * ITEMS_PER_PAGE

    # Fetch nodes from the database with the calculated offset and limit (fixed at 100)
    nodes = await app.db.get_nodes(offset=offset, limit=ITEMS_PER_PAGE)

    # Handle case when no nodes are found
    if not nodes:
        raise HTTPException(status_code=404, detail="No nodes found")

    return nodes


@app.get("/api/v1/nodes/all", response_model=List[NodeDBModel])
async def get_all_nodes() -> int:
    """
    Get all nodes
    """
    if not hasattr(app, "db"):
        raise HTTPException(status_code=500, detail="Database not initialized")

    nodes = await app.db.get_all_nodes()

    if not nodes:
        raise HTTPException(status_code=404, detail="No nodes found")

    return nodes


@app.get("/api/v1/nodes/filter/{filter_input}", response_model=List[NodeDBModel])
async def get_nodes_filtered(filter_input: str) -> List[NodeDBModel]:
    """
    Get nodes filtered by a string, get it from all nodes, not paginated.
    The filter can be a range like '1-3' or comma-separated values like '1,2,3'.
    """
    nodes = await app.db.get_all_nodes()
    filtered_nodes = []

    # Split the filter string by comma and process each part
    filter_parts = filter_input.split(",")
    for part in filter_parts:
        part = part.strip()  # Trim whitespace
        if "-" in part:
            # Handle range like '1-3'
            start, end = part.split("-")
            try:
                start_id = int(start.strip())
                end_id = int(end.strip())
                filtered_nodes.extend(
                    node for node in nodes if start_id <= node.id <= end_id
                )
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Invalid range in filter"
                ) from ValueError
        else:
            # Handle single ID
            try:
                node_id = int(part)
                node = next((node for node in nodes if node.id == node_id), None)
                if node:
                    filtered_nodes.append(node)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Invalid ID in filter"
                ) from ValueError
    return filtered_nodes


# API endpoint to get all subcases
@app.get("/api/v1/subcases", response_model=List[SubcaseDBModel])
async def get_subcases() -> List[SubcaseDBModel]:
    """Get all subcases"""
    if not hasattr(app, "db"):
        raise HTTPException(status_code=500, detail="Database not initialized")
    return await app.db.get_subcases()


@app.post("/api/v1/upload-chunk")
async def upload_chunk(
    file: UploadFile, filename: str = Form(...), offset: int = Form(...)
):
    """
    Upload a chunk of a file
    """
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # check if the file exists, if so, delete it
    if os.path.exists(file_path):
        os.remove(file_path)

    # Create the upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Open the file in append mode to write the chunk at the correct offset
    with open(file_path, "ab") as f:
        f.seek(offset)
        content = await file.read()
        f.write(content)

    return {"message": "Chunk uploaded successfully!"}


@app.post("/api/v1/run-extractor")
async def run_extractor(request: RunExtractorRequest):
    """
    Run the extractor. This is the main endpoint to run the program
    """
    fem_file = request.fem_filename
    mpcf_file = request.mpcf_filename

    print(f"Running extractor with files: {fem_file}, {mpcf_file}")

    # Clear all Instances
    Node.reset()
    Element1D.reset()
    Element.reset_graph()
    Subcase.reset()
    MPC.reset()

    blocksize = 8
    model_output_folder = OUTPUT_FOLDER + "/" + f"FRONTEND_{fem_file.split('.')[0]}"

    mpc_force_extractor = MPCForceExtractor(
        UPLOAD_FOLDER + f"/{fem_file}",
        UPLOAD_FOLDER + f"/{mpcf_file}",
        model_output_folder,
    )

    # Write Summary
    mpc_force_extractor.build_fem_and_subcase_data(blocksize)
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


@app.post("/api/v1/import-db")
async def import_db(request: DatabaseRequest):
    """
    Import a database (db) file and reinitialize the database
    """
    # Get the uploaded file
    db_file = request.database_filename

    db_path = UPLOAD_FOLDER + "/" + db_file

    # Check if the file exists
    if not os.path.exists(db_path):
        raise HTTPException(
            status_code=404, detail=f"Database file {db_file} not found"
        )

    # Reinitialize the database
    if not hasattr(app, "db"):
        app.db = MPCDatabase(db_path)
    app.db.reinitialize_db(db_path)
    return {"message": "Database imported successfully!"}


# HMTL Section
# Route for the main page (MPC list)
@app.get("/mpcs", response_class=HTMLResponse)
async def read_mpcs(request: Request):
    """Render the mpcs.html template"""
    return templates.TemplateResponse("mpcs.html", {"request": request})


# Route for nodes view (HTML)
@app.get("/nodes", response_class=HTMLResponse)
async def read_nodes(request: Request):
    """Render the nodes.html template"""
    return templates.TemplateResponse("nodes.html", {"request": request})


# Route for main view (HTML)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the nodes.html template"""
    return templates.TemplateResponse("main.html", {"request": request})
