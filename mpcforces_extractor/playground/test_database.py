import pytest
from mpcforces_extractor.playground.database import FakeMPCDatabase
from fastapi import HTTPException


@pytest.fixture
def db():
    return FakeMPCDatabase()


@pytest.mark.asyncio
async def test_initialize_database(db):
    assert len(await db.get_mpcs()) == 2  # Check initial population


@pytest.mark.asyncio
async def test_get_mpc(db):
    mpc = await db.get_mpc(1)  # Await the async function
    assert mpc.id == 1
    assert mpc.config == "RBE2"


@pytest.mark.asyncio
async def test_remove_mpc(db):
    await db.remove_mpc(1)  # Await the async function
    with pytest.raises(HTTPException):
        await db.get_mpc(1)  # Await the async function
