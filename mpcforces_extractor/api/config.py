import os
from pathlib import Path
import importlib.resources

# Constants
ITEMS_PER_PAGE = 100

# Webserver Folders
# Use importlib.resources.files() to get paths
STATIC_DIR = importlib.resources.files("mpcforces_extractor.frontend").joinpath(
    "static"
)
TEMPLATES_DIR = importlib.resources.files("mpcforces_extractor.frontend").joinpath(
    "templates"
)

# Data Folders
CWD = os.getcwd()
DATA_DIR = Path(CWD) / "data"

# Create data directory if it does not exist
DATA_DIR.mkdir(exist_ok=True)

# Define and create upload and output folders
UPLOAD_FOLDER = DATA_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

OUTPUT_FOLDER = DATA_DIR / "output"
OUTPUT_FOLDER.mkdir(exist_ok=True)
