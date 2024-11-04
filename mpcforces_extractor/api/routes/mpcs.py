from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from mpcforces_extractor.api.db.database import MPCDBModel
from mpcforces_extractor.api.dependencies import get_db

router = APIRouter()


# API endpoint to get all MPCs
@router.get("", response_model=List[MPCDBModel])
async def get_mpcs(db=Depends(get_db)) -> List[MPCDBModel]:
    """Get all MPCs"""

    return await db.get_mpcs()


# API endpoint to get a specific MPC by ID
@router.get("/{mpc_id}", response_model=MPCDBModel)
async def get_mpc(mpc_id: int, db=Depends(get_db)) -> MPCDBModel:
    """Get info about a specific MPC"""

    mpc = await db.get_mpc(mpc_id)
    if mpc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MPC with id: {mpc_id} does not exist",
        )

    return mpc


# API endpoint to remove an MPC by ID
@router.delete("/{mpc_id}")
async def remove_mpc(mpc_id: int, db=Depends(get_db)):
    """Remove an MPC"""
    await db.remove_mpc(mpc_id)
    return {"message": f"MPC with id: {mpc_id} removed"}
