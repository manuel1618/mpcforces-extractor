import os
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, HTTPException, Request
from mpcforces_extractor.api.config import UPLOAD_FOLDER, TEMPLATES_DIR
from mpcforces_extractor.api.db.database import MPCDatabase
from mpcforces_extractor.api.db.schemas import DatabaseRequest

templates = Jinja2Templates(directory=TEMPLATES_DIR)
router = APIRouter()


@router.post("/import-db")
async def import_db(request: Request, db_request: DatabaseRequest):
    """
    Import a database (db) file and reinitialize the database
    """
    # Get the uploaded file
    db_file = db_request.database_filename

    db_path = UPLOAD_FOLDER + "/" + db_file

    # Check if the file exists
    if not os.path.exists(db_path):
        raise HTTPException(
            status_code=404, detail=f"Database file {db_file} not found"
        )

    app = request.app

    # Reinitialize the database
    if not hasattr(app, "db"):
        app.db = MPCDatabase(db_path)
    app.db.reinitialize_db(db_path)
    return {"message": "Database imported successfully!"}
