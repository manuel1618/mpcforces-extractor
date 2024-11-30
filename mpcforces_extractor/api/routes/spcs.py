from typing import List
from fastapi import APIRouter, Depends
from mpcforces_extractor.api.dependencies import get_db
from mpcforces_extractor.api.db.database import SPCDBModel

router = APIRouter()


# API endpoint to get all SPCs
@router.get("", response_model=List[SPCDBModel])
async def get_spcs(db=Depends(get_db)) -> List[SPCDBModel]:
    """Get all SPCs"""

    return await db.get_spcs()
