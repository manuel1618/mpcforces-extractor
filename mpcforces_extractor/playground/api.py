from typing import List
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from mpcforces_extractor.playground.database import FakeMPCDatabase, MPCDBModel

app = FastAPI()
db = FakeMPCDatabase()

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


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the index.html template"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/v1/mpcs", response_model=List[MPCDBModel])
async def get_mpcs() -> List[MPCDBModel]:
    """Get all MPCs"""
    return await db.get_mpcs()


@app.get("/api/v1/mpcs/{id}", response_model=MPCDBModel)
async def get_mpc(mpc_id: int) -> MPCDBModel:
    """Get info about a planet

    Args:
        name: Name of the planet
    """
    mpc = await db.get_mpc(mpc_id)
    if mpc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MPC, id: {mpc_id} does not exist",
        )

    return mpc
