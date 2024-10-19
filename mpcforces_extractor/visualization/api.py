from typing import List
from fastapi import FastAPI, HTTPException, status, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from mpcforces_extractor.database.database import (
    MPCDatabase,
    MPCDBModel,
    NodeDBModel,
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


# Route for the main page (MPC list)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the mpcs.html template"""
    return templates.TemplateResponse("mpcs.html", {"request": request})


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


# Route for nodes view (HTML)
@app.get("/nodes", response_class=HTMLResponse)
async def read_nodes(request: Request):
    """Render the nodes.html template"""
    return templates.TemplateResponse("nodes.html", {"request": request})
