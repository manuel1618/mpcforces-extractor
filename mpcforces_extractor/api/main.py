from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mpcforces_extractor.api.routes import (
    database,
    extractor,
    file_upload,
    html_routes,
    nodes,
    rbe2s,
    subcases,
)
from mpcforces_extractor.api.config import STATIC_DIR, TEMPLATES_DIR


# Setup Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app = FastAPI(redirect_slashes=False)

# Mount the static files directory
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

# Include routers with prefixes
app.include_router(rbe2s.router, prefix="/api/v1/rbe2s", tags=["rbe2s"])
app.include_router(rbe2s.router, prefix="/api/v1/rbe3s", tags=["rbe3s"])
app.include_router(nodes.router, prefix="/api/v1/nodes", tags=["nodes"])
app.include_router(subcases.router, prefix="/api/v1/subcases", tags=["subcases"])
app.include_router(file_upload.router, prefix="/api/v1", tags=["file_upload"])
app.include_router(extractor.router, prefix="/api/v1", tags=["extractor"])
app.include_router(database.router, prefix="/api/v1", tags=["database"])
app.include_router(html_routes.router, tags=["html_routes"])
