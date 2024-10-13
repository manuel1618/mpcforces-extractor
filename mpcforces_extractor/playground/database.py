from abc import ABC, abstractmethod
from typing import List, Dict
from fastapi import HTTPException
from sqlmodel import Session, create_engine, SQLModel, Field, select, Column, JSON
from mpcforces_extractor.datastructure.rigids import MPC
from mpcforces_extractor.datastructure.rigids import MPC_CONFIG
from mpcforces_extractor.datastructure.entities import Node, Element


class MPCDBModel(SQLModel, table=True):
    """
    Database Representation of MPC Class
    """

    id: int = Field(primary_key=True)
    config: str = Field()  # Store MPC_CONFIG as a string
    master_node: int = Field()  # Store master node as an integer
    nodes: str = Field()  # Store nodes as a string
    part_id2nodes: Dict = Field(
        default_factory=dict, sa_column=Column(JSON)
    )  # Store part_id2nodes as a dictionary

    def to_mpc(self):
        """
        Method to convert MPCDBModel back to MPC object if needed
        """
        print(f"Converting MPCDBModel to MPC: id={self.id}, nodes={self.nodes}")
        nodes_list = (
            str(self.nodes).split(",") if self.nodes else []
        )  # Add a check to avoid splitting None
        mpc = MPC(
            element_id=self.id,
            mpc_config=MPC_CONFIG[self.config],  # Convert string back to enum
            master_node=Node.node_id2node[
                self.master_node
            ],  # Handle node conversion as needed
            nodes=[Node.node_id2node[int(node_id)] for node_id in nodes_list],
            dofs="",
        )
        mpc.part_id2node_ids = self.part_id2nodes
        return mpc


class NodeDBModel(SQLModel, table=True):
    """
    Database Representation of Node Instance
    """

    id: int = Field(primary_key=True)
    coord_x: float = Field()
    coord_y: float = Field()
    coord_z: float = Field()

    def to_node(self):
        """
        Method to convert NodeDBModel back to Node object if needed
        """
        return Node(node_id=self.id, coords=[self.coord_x, self.coord_y, self.coord_z])


class MPCForcesExtractorDatabase(ABC):
    """
    This class represents a generic MPC database.
    """

    @abstractmethod
    async def get_mpcs(self) -> List[MPCDBModel]:
        """
        Get all MPCs
        """
        raise NotImplementedError


class FakeDatabase(MPCForcesExtractorDatabase):
    """
    A fake Database used for development
    """

    def __init__(self):
        """
        Development database creation and population
        """
        # Create the SQLite engine
        self.engine = create_engine("sqlite:///db.db")

        # Drop existing tables for development purposes
        SQLModel.metadata.drop_all(self.engine)

        # Create the tables
        SQLModel.metadata.create_all(self.engine)

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
        self.populate_database()

        # Read from the database
        with Session(self.engine) as session:
            statement = select(MPCDBModel)
            self.mpcs = {mpc.id: mpc for mpc in session.exec(statement).all()}
            print(self.mpcs)

    def populate_database(self):
        """
        Function to populate the database from MPC instances
        """
        with Session(self.engine) as session:
            for node in Node.node_id2node.values():
                db_node = NodeDBModel(
                    id=node.id,
                    coord_x=node.coords[0],
                    coord_y=node.coords[1],
                    coord_z=node.coords[2],
                )
                session.add(db_node)

            for mpc in MPC.id_2_instance.values():

                mpc.get_part_id2force(None)

                # Convert MPC instance to MPCDBModel
                db_mpc = MPCDBModel(
                    id=mpc.element_id,
                    config=mpc.mpc_config.name,  # Store enum as string
                    master_node=mpc.master_node.id,
                    nodes=",".join([str(node.id) for node in mpc.nodes]),
                    part_id2nodes=mpc.part_id2node_ids,
                )
                # Add to the session
                session.add(db_mpc)

            # Commit to the database
            session.commit()

    async def get_mpcs(self) -> List[MPCDBModel]:
        """
        Get all MPCs
        """
        return list(self.mpcs.values())

    async def get_mpc(self, mpc_id: int) -> MPCDBModel:
        """
        Get a specific MPC
        """
        if mpc_id in self.mpcs:
            return self.mpcs.get(mpc_id)
        raise HTTPException(
            status_code=404, detail=f"MPC with id {mpc_id} does not exist"
        )

    async def get_nodes(self) -> List[NodeDBModel]:
        """
        Get all nodes
        """
        with Session(self.engine) as session:
            statement = select(NodeDBModel)
            return session.exec(statement).all()

    async def remove_mpc(self, mpc_id: int):
        """
        Remove a specific MPC
        """
        if mpc_id in self.mpcs:
            del self.mpcs[mpc_id]
        else:
            raise HTTPException(
                status_code=404, detail=f"MPC with id {mpc_id} does not exist"
            )
