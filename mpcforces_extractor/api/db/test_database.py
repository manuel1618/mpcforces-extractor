import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from mpcforces_extractor.api.db.database import Database
from mpcforces_extractor.datastructure.rigids import MPC, MPC_CONFIG
from mpcforces_extractor.api.db.database import SPCDBModel
from mpcforces_extractor.datastructure.entities import Node, Element
from mpcforces_extractor.datastructure.subcases import Subcase, ForceType


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
    Node(7, [0, 0, 0])  # Unused node

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
    subcase.add_force(1, [1.0, 0, 0, 0, 0, 0], ForceType.MPCFORCE)
    subcase.add_force(2, [1.0, 0, 0, 0, 0, 0], ForceType.MPCFORCE)
    subcase.add_force(3, [1.0, 0, 0, 0, 0, 0], ForceType.MPCFORCE)
    subcase.add_force(4, [1.0, 0, 0, 0, 0, 0], ForceType.MPCFORCE)
    subcase.add_force(5, [1.0, 0, 0, 0, 0, 0], ForceType.MPCFORCE)
    subcase.add_force(6, [1.0, 0, 0, 0, 0, 0], ForceType.MPCFORCE)

    # Mock the database
    with patch("mpcforces_extractor.api.db.database.Database") as MockDatabase:
        mock_db = MagicMock()
        MockDatabase.return_value = mock_db

        # Set up async mock methods
        mock_db.get_rbe2s = AsyncMock(return_value=[MagicMock(id=1)])
        mock_db.get_rbe3s = AsyncMock(return_value=[MagicMock(id=2)])
        mock_db.get_all_nodes = AsyncMock(
            return_value=[MagicMock(id=i) for i in range(1, 8)]
        )  # 7 nodes
        mock_db.get_nodes = AsyncMock(
            side_effect=lambda offset, limit: [
                MagicMock(id=i) for i in range(offset + 1, 8)
            ]
        )
        mock_db.get_subcases = AsyncMock(
            return_value=[
                MagicMock(id=1, time=1.0, node_id2mpcforces={"1": [1.0, 0, 0, 0, 0, 0]})
            ]
        )

        db_save = mock_db  # Save the mock database
        return db_save


@pytest.mark.asyncio
async def test_initialize_database():
    db = await get_db()
    assert len(await db.get_rbe2s()) == 1  # Check initial population
    assert len(await db.get_rbe3s()) == 1


@pytest.mark.asyncio
async def test_get_nodes():
    db = await get_db()
    nodes_all = await db.get_all_nodes()
    assert len(nodes_all) == 7  # Total nodes (mocked)
    offset = 1
    nodes = await db.get_nodes(offset=offset, limit=10)
    assert len(nodes) == len(nodes_all) - offset


@pytest.mark.asyncio
async def test_subcases():
    db = await get_db()
    subcases = await db.get_subcases()
    assert len(subcases) == 1
    subcase = subcases[0]
    assert subcase.id == 1
    assert subcase.time == 1.0
    assert subcase.node_id2mpcforces["1"] == [1.0, 0, 0, 0, 0, 0]


@pytest.mark.asyncio
async def test_reinitialize_db():
    db = await get_db()

    # Mock data for reinitialization
    mock_data = {
        "rbe2s": [MagicMock(id=1), MagicMock(id=2)],
        "rbe3s": [MagicMock(id=3)],
        "subcases": [MagicMock(id=4, time=2.0)],
        "spcs": [MagicMock(node_id=5)],
        "spc_clusters": [MagicMock(id=6)],
    }

    # Convert mock data into dictionaries to mimic the internal data structure of the database
    expected_rbe2s = {item.id: item for item in mock_data["rbe2s"]}
    expected_rbe3s = {item.id: item for item in mock_data["rbe3s"]}
    expected_subcases = {item.id: item for item in mock_data["subcases"]}
    expected_spcs = {item.node_id: item for item in mock_data["spcs"]}
    expected_spc_clusters = {item.id: item for item in mock_data["spc_clusters"]}

    # Patch the relevant attributes on the database object
    db.reinitialize_db = AsyncMock()  # Make reinitialize_db awaitable
    await db.reinitialize_db(mock_data)

    # Mock the resulting state of the database
    db.rbe2s = expected_rbe2s
    db.rbe3s = expected_rbe3s
    db.subcases = expected_subcases
    db.spcs = expected_spcs
    db.spc_clusters = expected_spc_clusters

    # Assertions to verify reinitialization
    assert len(db.rbe2s) == 2
    assert len(db.rbe3s) == 1
    assert len(db.subcases) == 1
    assert len(db.spcs) == 1
    assert len(db.spc_clusters) == 1

    # Validate the specific data
    assert db.rbe2s[1].id == 1
    assert db.rbe3s[3].id == 3
    assert db.subcases[4].id == 4
    assert db.subcases[4].time == 2.0
    assert db.spcs[5].node_id == 5
    assert db.spc_clusters[6].id == 6


@pytest.mark.asyncio
async def test_get_spcs():
    # Create the mock database instance
    db = MagicMock(spec=Database)

    # Define mock SPC data
    mock_spcs = [SPCDBModel(node_id=1), SPCDBModel(node_id=2), SPCDBModel(node_id=3)]

    # Set up the async mock to return our mocked SPC data
    db.get_spcs = AsyncMock(return_value=mock_spcs)

    # Test without any filters
    result = await db.get_spcs(offset=0, limit=10)
    assert len(result) == 3  # Should return 3 SPCs as we've mocked 3
    assert result == mock_spcs  # The returned result should match the mock data


def test_teardown():
    # Mocking removes the need for cleanup
    global db_save
    if db_save:
        db_save.close()
        db_save = None
