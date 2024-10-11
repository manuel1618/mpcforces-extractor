from fastapi import FastAPI, HTTPException, status
from mpcforces_extractor.playground.database import FakeMPCDatabase, MPCDBModel

app = FastAPI()
db = FakeMPCDatabase()


@app.get("/api/v1/mpcs/{id}", response_model=MPCDBModel)
async def get_mpc(mpc_id: int) -> MPCDBModel:
    """Get info about a planet

    Args:
        name: Name of the planet
    """
    mpc = await db.get_mpc(mpc_id)
    if mpc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MPC, id: {mpc_id} does not exist",
        )

    return mpc
