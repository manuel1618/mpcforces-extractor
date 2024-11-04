import os
import pytest
from mpcforces_extractor.api.db.database import MPCDatabase
from mpcforces_extractor.datastructure.rigids import MPC, MPC_CONFIG
from mpcforces_extractor.datastructure.entities import Node, Element
from mpcforces_extractor.datastructure.subcases import Subcase
from fastapi import HTTPException

# Initialize db_save at the module level
db_save = None  # Ensure db_save is defined before use


@pytest.mark.asyncio
async def get_db():
    global db_save  # Declare db_save as global to modify it

    if db_save:
        return db_save

    # Define the initial MPC instances
    node1 = Node(1, [0, 0, 0])
    node2 = Node(2, [1, 2, 3])
    node3 = Node(3, [4, 5, 6])
    node4 = Node(4, [0, 0, 0])
    node5 = Node(5, [1, 2, 3])
    node6 = Node(6, [4, 5, 6])
    node7 = Node(7, [0, 0, 0])  # Unused node

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

    subcase = Subcase(1, 1.0)
    subcase.add_force(1, [1.0, 0, 0, 0, 0, 0])
    subcase.add_force(2, [1.0, 0, 0, 0, 0, 0])
    subcase.add_force(3, [1.0, 0, 0, 0, 0, 0])
    subcase.add_force(4, [1.0, 0, 0, 0, 0, 0])
    subcase.add_force(5, [1.0, 0, 0, 0, 0, 0])
    subcase.add_force(6, [1.0, 0, 0, 0, 0, 0])

    db = MPCDatabase("test.db")
    db.populate_database()
    db_save = db  # Save the initialized database
    return db_save


@pytest.mark.asyncio
async def test_initialize_database():
    db = await get_db()
    assert len(await db.get_mpcs()) == 2  # Check initial population


@pytest.mark.asyncio
async def test_get_mpc():
    db = await get_db()
    mpc = await db.get_mpc(1)  # Await the async function
    assert mpc.id == 1
    assert mpc.config == "RBE2"


@pytest.mark.asyncio
async def test_remove_mpc():
    db = await get_db()
    await db.remove_mpc(1)  # Await the async function
    with pytest.raises(HTTPException):
        await db.get_mpc(1)  # Await the async function


@pytest.mark.asyncio
async def test_remove_mpc_not_exist():
    db = await get_db()
    with pytest.raises(HTTPException):
        await db.remove_mpc(3)


@pytest.mark.asyncio
async def test_get_nodes():
    db = await get_db()
    nodes_all = await db.get_all_nodes()
    assert len(nodes_all) == 6
    offset = 1
    nodes = await db.get_nodes(offset, 100)
    assert len(nodes) == len(nodes_all) - offset

    db.populate_database(load_all_nodes=True)
    assert len(await db.get_all_nodes()) == 7


@pytest.mark.asyncio
async def test_subcases():
    db = await get_db()
    subcases = await db.get_subcases()
    assert len(subcases) == 1
    subcase = subcases[0]
    assert subcase.id == 1
    assert subcase.time == 1.0
    assert subcase.node_id2forces["1"] == [1.0, 0, 0, 0, 0, 0]


# remove the db.db after all test
def test_teardown():
    db_save.close()
    os.remove("test.db")
