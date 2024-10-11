from abc import ABC, abstractmethod
from typing import List
from fastapi import HTTPException
from sqlmodel import Session, create_engine, SQLModel, Field, select
from mpcforces_extractor.datastructure.rigids import MPC
from mpcforces_extractor.datastructure.rigids import MPC_CONFIG


class MPCDBModel(SQLModel, table=True):
    """
    Database Representation of MPC Class
    """

    id: int = Field(primary_key=True)
    config: str = Field()  # Store MPC_CONFIG as a string
    master_node: int
    nodes: str

    def to_mpc(self):
        """
        Method to convert MPCDBModel back to MPC object if needed
        """
        return MPC(
            element_id=self.id,
            mpc_config=MPC_CONFIG[self.config],  # Convert string back to enum
            master_node=self.master_node,
            nodes=self.nodes.split(","),  # Handle node conversion as needed
            dofs="",
        )


class MPCDatabase(ABC):
    """
    This class represents a generic MPC database.
    """

    @abstractmethod
    async def get_mpcs(self) -> List[MPCDBModel]:
        """
        Get all MPCs
        """
        raise NotImplementedError


class FakeMPCDatabase(MPCDatabase):
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
        mpcs = [
            MPC(
                element_id=1,
                mpc_config=MPC_CONFIG.RBE2,
                master_node=1,
                nodes=[],
                dofs="",
            ),
            MPC(
                element_id=2,
                mpc_config=MPC_CONFIG.RBE3,
                master_node=3,
                nodes=[],
                dofs="",
            ),
        ]
        self.populate_database_from_mpc(mpcs)

        # Read from the database
        with Session(self.engine) as session:
            statement = select(MPCDBModel)
            self.mpcs = {mpc.id: mpc for mpc in session.exec(statement).all()}

    def populate_database_from_mpc(self, mpcs: List[MPC]):
        """
        Function to populate the database from MPC instances
        """
        with Session(self.engine) as session:
            for mpc in mpcs:
                # Convert MPC instance to MPCDBModel
                db_mpc = MPCDBModel(
                    id=mpc.element_id,
                    config=mpc.mpc_config.name,  # Store enum as string
                    master_node=mpc.master_node,
                    nodes=",".join([str(node.id) for node in mpc.nodes]),
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
