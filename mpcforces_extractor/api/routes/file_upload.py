import os
from fastapi import APIRouter, UploadFile, Form
from mpcforces_extractor.api.config import UPLOAD_FOLDER, OUTPUT_FOLDER

router = APIRouter()


@router.post("/upload-chunk")
async def upload_chunk(
    file: UploadFile, filename: str = Form(...), offset: int = Form(...)
):
    """
    Upload a chunk of a file
    """
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # check if the file exists, if so, delete it
    if offset == 0:
        if os.path.exists(file_path):
            os.remove(file_path)

    # Create the upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Open the file in append mode to write the chunk at the correct offset
    with open(file_path, "ab") as f:
        f.seek(offset)
        content = await file.read()
        f.write(content)

    return {"message": "Chunk uploaded successfully!"}


@router.get("/get-output-folder")
async def get_output_folder():
    """
    Get the output folder path
    """
    return {"output_folder": OUTPUT_FOLDER}
