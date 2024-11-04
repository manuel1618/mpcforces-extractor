import os
from pathlib import Path

ITEMS_PER_PAGE = 100

# Wwebserer Folders
PACKAGE_ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = f"{PACKAGE_ROOT_DIR}/frontend/static"  # Path to the static directory
TEMPLATES_DIR = (
    f"{PACKAGE_ROOT_DIR}/frontend/templates"  # Path to the templates directory
)

# Data Folders
CWD = os.getcwd()
DATA_DIR = f"{CWD}/data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
UPLOAD_FOLDER = f"{DATA_DIR}/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
OUTPUT_FOLDER = f"{DATA_DIR}/output"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
