from typing import List
from fastapi import FastAPI, HTTPException, status, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from mpcforces_extractor.database.database import (
    MPCDatabase,
    MPCDBModel,
    NodeDBModel,
    SubcaseDBModel,
)

ITEMS_PER_PAGE = 100  # Define a fixed number of items per page


# Setup Jinja2 templates
templates = Jinja2Templates(
    directory="mpcforces_extractor/visualization/frontend/templates"
)


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """
    Connect to the database when the application starts
    """
    print("Connecting to the database")
    app.db = MPCDatabase()


# Mount the static files directory
app.mount(
    "/static",
    StaticFiles(directory="mpcforces_extractor/visualization/frontend/static"),
    name="static",
)


# API endpoint to get all MPCs
@app.get("/api/v1/mpcs", response_model=List[MPCDBModel])
async def get_mpcs() -> List[MPCDBModel]:
    """Get all MPCs"""
    return await app.db.get_mpcs()


# API endpoint to get a specific MPC by ID
@app.get("/api/v1/mpcs/{mpc_id}", response_model=MPCDBModel)
async def get_mpc(mpc_id: int) -> MPCDBModel:
    """Get info about a specific MPC"""
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
    await app.db.remove_mpc(mpc_id)
    return {"message": f"MPC with id: {mpc_id} removed"}


@app.get("/api/v1/nodes", response_model=List[NodeDBModel])
async def get_nodes(page: int = Query(1, ge=1)) -> List[NodeDBModel]:
    """
    Get nodes with pagination (fixed 100 items per page)
    """
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
    return await app.db.get_subcases()


# HMTL Section
# Route for the main page (MPC list)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the mpcs.html template"""
    return templates.TemplateResponse("mpcs.html", {"request": request})


# Route for nodes view (HTML)
@app.get("/nodes", response_class=HTMLResponse)
async def read_nodes(request: Request):
    """Render the nodes.html template"""
    return templates.TemplateResponse("nodes.html", {"request": request})
