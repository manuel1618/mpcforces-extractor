from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from mpcforces_extractor.api.config import TEMPLATES_DIR

templates = Jinja2Templates(directory=TEMPLATES_DIR)
router = APIRouter()


# Route for the main page (MPC list)
@router.get("/mpcs", response_class=HTMLResponse)
async def read_mpcs(request: Request):
    """Render the mpcs.html template"""
    return templates.TemplateResponse("mpcs.html", {"request": request})


# Route for nodes view (HTML)
@router.get("/nodes", response_class=HTMLResponse)
async def read_nodes(request: Request):
    """Render the nodes.html template"""
    return templates.TemplateResponse("nodes.html", {"request": request})


# Route for main view (HTML)
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the nodes.html template"""
    return templates.TemplateResponse("main.html", {"request": request})


# Route for SPC view (HTML)
@router.get("/spcs", response_class=HTMLResponse)
async def read_spcs(request: Request):
    """Render the spcs.html template"""
    return templates.TemplateResponse("spcs.html", {"request": request})


# Route for SPC Cluster view (HTML)
@router.get("/spcclusters", response_class=HTMLResponse)
async def read_spc_clusters(request: Request):
    """Render the spcclusters.html template"""
    return templates.TemplateResponse("spcclusters.html", {"request": request})
