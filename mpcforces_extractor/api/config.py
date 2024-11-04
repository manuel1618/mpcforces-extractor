from pathlib import Path

ITEMS_PER_PAGE = 100
PACKAGE_ROOT_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = f"{PACKAGE_ROOT_DIR}/data/uploads"
OUTPUT_FOLDER = f"{PACKAGE_ROOT_DIR}/data/output"
STATIC_DIR = f"{PACKAGE_ROOT_DIR}/frontend/static"  # Path to the static directory
TEMPLATES_DIR = (
    f"{PACKAGE_ROOT_DIR}/frontend/templates"  # Path to the templates directory
)
