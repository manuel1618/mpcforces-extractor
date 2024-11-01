from typing import List
from fastapi import APIRouter, Depends
from mpcforces_extractor.api.dependencies import get_db
from mpcforces_extractor.api.db.database import SubcaseDBModel

router = APIRouter()


@router.get("", response_model=List[SubcaseDBModel])
async def get_subcases(db=Depends(get_db)) -> List[SubcaseDBModel]:
    """Get all subcases"""
    return await db.get_subcases()
