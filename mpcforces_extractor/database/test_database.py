import pytest
from mpcforces_extractor.database.database import MPCDatabase
from mpcforces_extractor.datastructure.rigids import MPC, MPC_CONFIG
from mpcforces_extractor.datastructure.entities import Node, Element

from fastapi import HTTPException


# Define the initial MPC instances
node1 = Node(1, [0, 0, 0])
node2 = Node(2, [1, 2, 3])
node3 = Node(3, [4, 5, 6])
node4 = Node(4, [0, 0, 0])
node5 = Node(5, [1, 2, 3])
node6 = Node(6, [4, 5, 6])

MPC.reset()
MPC(
    element_id=1,
    mpc_config=MPC_CONFIG.RBE2,
    master_node=node1,
    nodes=[node2, node3],
    dofs="",
)
MPC(
    element_id=2,
    mpc_config=MPC_CONFIG.RBE3,
    master_node=node4,
    nodes=[node5, node6],
    dofs="",
)

Element(1, 1, [node2, node3])
Element(2, 2, [node6, node5])


db = MPCDatabase("db.db")
db.populate_database()


@pytest.mark.asyncio
async def test_initialize_database():
    assert len(await db.get_mpcs()) == 2  # Check initial population


@pytest.mark.asyncio
async def test_get_mpc():
    mpc = await db.get_mpc(1)  # Await the async function
    assert mpc.id == 1
    assert mpc.config == "RBE2"


@pytest.mark.asyncio
async def test_remove_mpc():
    await db.remove_mpc(1)  # Await the async function
    with pytest.raises(HTTPException):
        await db.get_mpc(1)  # Await the async function
