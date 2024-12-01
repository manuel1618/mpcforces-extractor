from typing import List
from fastapi import APIRouter, Depends
from mpcforces_extractor.api.db.database import RBE2DBModel
from mpcforces_extractor.api.dependencies import get_db

router = APIRouter()


# API endpoint to get all MPCs
@router.get("", response_model=List[RBE2DBModel])
async def get_rbe2s(db=Depends(get_db)) -> List[RBE2DBModel]:
    """Get all MPCs"""
    return await db.get_rbe2s()
