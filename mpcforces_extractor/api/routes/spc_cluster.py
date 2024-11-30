from typing import List
from fastapi import APIRouter, Depends
from mpcforces_extractor.api.dependencies import get_db
from mpcforces_extractor.api.db.database import SPCClusterDBModel

router = APIRouter()


# API endpoint to get all SPC Cluster
@router.get("", response_model=List[SPCClusterDBModel])
async def get_spc_clusters(db=Depends(get_db)) -> List[SPCClusterDBModel]:
    """Get all SPC Clusters"""
    return await db.get_spc_clusters()
