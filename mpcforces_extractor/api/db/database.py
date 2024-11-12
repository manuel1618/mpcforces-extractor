from typing import List
from fastapi import HTTPException
from sqlmodel import Session, create_engine, SQLModel, select, text
from mpcforces_extractor.datastructure.rigids import MPC
from mpcforces_extractor.datastructure.entities import Node
from mpcforces_extractor.datastructure.subcases import Subcase
from mpcforces_extractor.api.db.models import (
    RBE2DBModel,
    RBE3DBModel,
    NodeDBModel,
    SubcaseDBModel,
)
from mpcforces_extractor.datastructure.rigids import MPC_CONFIG


class MPCDatabase:
    """
    A Database class to store MPC instances, Nodes and Subcases
    """

    def __init__(self, file_path: str):
        """
        Development database creation and population
        """

        # Initialize the database
        self.engine = None
        self.rbe2s = {}
        self.rbe3s = {}
        self.subcases = {}

        self.engine = create_engine(f"sqlite:///{file_path}")

    def close(self):
        """
        Close the database connection
        """
        self.engine.dispose()
        self.engine = None

    def reinitialize_db(self, file_path: str):
        """
        Reinitialize the database with the data from the file
        """
        self.engine = create_engine(f"sqlite:///{file_path}")
        with Session(self.engine) as session:
            self.rbe2s = {
                rbe2.id: rbe2 for rbe2 in session.exec(select(RBE2DBModel)).all()
            }
            self.rbe3s = {
                rbe3.id: rbe3 for rbe3 in session.exec(select(RBE3DBModel)).all()
            }
            self.subcases = {
                subcase.id: subcase
                for subcase in session.exec(select(SubcaseDBModel)).all()
            }

    def populate_database(self, load_all_nodes=False):
        """
        Function to populate the database from MPC instances
        """
        # delete the existing data
        # drop all tables
        with Session(self.engine) as session:
            session.exec(text("DROP TABLE IF EXISTS RBE2DBModel"))
            session.exec(text("DROP TABLE IF EXISTS RBE3DBModel"))
            session.exec(text("DROP TABLE IF EXISTS nodedbmodel"))
            session.exec(text("DROP TABLE IF EXISTS subcasedbmodel"))

        # Create the tables again
        SQLModel.metadata.create_all(self.engine)

        with Session(self.engine) as session:

            self.populate_nodes(load_all_nodes, session)

            self.populate_mpcs(session)

            # Populate Subcases
            for subcase in Subcase.subcases:
                db_subcase = SubcaseDBModel(
                    id=subcase.subcase_id,
                    node_id2forces=subcase.node_id2forces,
                    time=subcase.time,
                )
                session.add(db_subcase)

            # Commit to the database
            session.commit()

            self.rbe2s = {
                rbe2.id: rbe2 for rbe2 in session.exec(select(RBE2DBModel)).all()
            }
            self.rbe3s = {
                rbe3.id: rbe3 for rbe3 in session.exec(select(RBE3DBModel)).all()
            }
            self.subcases = {
                subcase.id: subcase
                for subcase in session.exec(select(SubcaseDBModel)).all()
            }

    def populate_nodes(self, load_all_nodes=False, session=None):
        """
        Function to populate the database with nodes
        """
        if load_all_nodes:  # Load in all the nodes
            for node in Node.node_id2node.values():
                db_node = NodeDBModel(
                    id=node.id,
                    coord_x=node.coords[0],
                    coord_y=node.coords[1],
                    coord_z=node.coords[2],
                )
                session.add(db_node)
        else:  # load in just the nodes that are used in the MPCs
            unique_nodes = set()
            for mpc_config in MPC_CONFIG:
                for mpc in MPC.config_2_id_2_instance[mpc_config.value].values():
                    for node in mpc.nodes:
                        unique_nodes.add(node)
                    unique_nodes.add(mpc.master_node)

            for node in unique_nodes:
                db_node = NodeDBModel(
                    id=node.id,
                    coord_x=node.coords[0],
                    coord_y=node.coords[1],
                    coord_z=node.coords[2],
                )
                session.add(db_node)

    def populate_mpcs(self, session):
        """
        Function to populate the database with MPCs
        """
        for mpc_config in MPC_CONFIG:
            for mpc in MPC.config_2_id_2_instance[mpc_config.value].values():
                mpc.get_part_id2force(None)
                sub2part2force = mpc.get_subcase_id2part_id2force()

                if mpc_config == MPC_CONFIG.RBE2:
                    db_mpc = RBE2DBModel(
                        id=mpc.element_id,
                        config=mpc.mpc_config.name,  # Store enum as string
                        master_node=mpc.master_node.id,
                        nodes=",".join([str(node.id) for node in mpc.nodes]),
                        part_id2nodes=mpc.part_id2node_ids,
                        subcase_id2part_id2forces=sub2part2force,
                    )
                elif mpc_config == MPC_CONFIG.RBE3:
                    db_mpc = RBE3DBModel(
                        id=mpc.element_id,
                        config=mpc.mpc_config.name,  # Store enum as string
                        master_node=mpc.master_node.id,
                        nodes=",".join([str(node.id) for node in mpc.nodes]),
                        part_id2nodes=mpc.part_id2node_ids,
                        subcase_id2part_id2forces=sub2part2force,
                    )
                else:
                    raise ValueError(f"Unknown MPC config {mpc_config}")
                # Add to the session
                session.add(db_mpc)

    async def get_rbe2s(self) -> List[RBE2DBModel]:
        """
        Get all MPCs
        """
        return list(self.rbe2s.values())

    async def get_rbe3s(self) -> List[RBE3DBModel]:
        """
        Get all MPCs
        """
        return list(self.rbe3s.values())

    async def get_nodes(self, offset: int, limit: int = 100) -> List[NodeDBModel]:
        """
        Get nodes for pagination
        """
        with Session(self.engine) as session:
            statement = select(NodeDBModel).offset(offset).limit(limit)
            return session.exec(statement).all()

    async def get_all_nodes(self) -> List[NodeDBModel]:
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

    async def get_subcases(self) -> List[SubcaseDBModel]:
        """
        Get all subcases
        """
        return list(self.subcases.values())
