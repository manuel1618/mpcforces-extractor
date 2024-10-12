from typing import List
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from mpcforces_extractor.playground.database import (
    FakeDatabase,
    MPCDBModel,
    NodeDBModel,
)

app = FastAPI()
db = FakeDatabase()

# Mount the static files directory
app.mount(
    "/static",
    StaticFiles(directory="mpcforces_extractor/playground/frontend/static"),
    name="static",
)

# Setup Jinja2 templates
templates = Jinja2Templates(
    directory="mpcforces_extractor/playground/frontend/templates"
)


# Route for the main page (MPC list)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the index.html template"""
    return templates.TemplateResponse("index.html", {"request": request})


# API endpoint to get all MPCs
@app.get("/api/v1/mpcs", response_model=List[MPCDBModel])
async def get_mpcs() -> List[MPCDBModel]:
    """Get all MPCs"""
    return await db.get_mpcs()


# API endpoint to get a specific MPC by ID
@app.get("/api/v1/mpcs/{mpc_id}", response_model=MPCDBModel)
async def get_mpc(mpc_id: int) -> MPCDBModel:
    """Get info about a specific MPC"""
    mpc = await db.get_mpc(mpc_id)
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
    await db.remove_mpc(mpc_id)
    return {"message": f"MPC with id: {mpc_id} removed"}


# API endpoint to get all nodes
@app.get("/api/v1/nodes", response_model=List[NodeDBModel])
async def get_nodes() -> List[NodeDBModel]:
    """Get all nodes"""
    return await db.get_nodes()


# Route for nodes view (HTML)
@app.get("/nodes", response_class=HTMLResponse)
async def read_nodes(request: Request):
    """Render the nodes.html template"""
    return templates.TemplateResponse("nodes.html", {"request": request})
