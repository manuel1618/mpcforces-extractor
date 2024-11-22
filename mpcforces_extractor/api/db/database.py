from typing import List, Optional
from fastapi import HTTPException
from sqlmodel import Session, create_engine, SQLModel, select, text
from sqlalchemy.sql.expression import asc, desc
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

    last_sort_column = "id"
    last_sort_direction = 1
    last_subcase_id = None
    last_query = None
    last_filter = None

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
                if mpc_config.value not in MPC.config_2_id_2_instance:
                    continue
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
            if mpc_config.value not in MPC.config_2_id_2_instance:
                continue
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

    async def get_nodes(
        self,
        *,
        offset: int,
        limit: int = 100,
        sort_column: str = "id",
        sort_direction: int = 1,
        node_ids: Optional[List[int]] = None,
        subcase_id: Optional[int] = None,
    ) -> List[NodeDBModel]:
        """
        Get nodes for pagination, sorting, and filtering.

        - offset: The offset for pagination.
        - limit: The limit for pagination (default: 100).
        - sort_column: The column to sort by (default: 'id').
        - sort_direction: The direction of sorting (1 for ascending, -1 for descending).
        - node_ids: An optional list of node IDs to filter by (default: None).
        """

        # Start a session with the database engine
        with Session(self.engine) as session:

            # early return if the last query is the same
            if self.last_query is not None:
                if (
                    self.last_sort_column == sort_column
                    and self.last_sort_direction == sort_direction
                    and self.last_filter == node_ids
                ):
                    return session.exec(
                        self.last_query.offset(offset).limit(limit)
                    ).all()

            # Create the base query
            query = select(NodeDBModel)

            # Apply filtering by node IDs if provided
            if node_ids:
                query = query.filter(NodeDBModel.id.in_(node_ids))

            # add force data if requested only if the subcase_id is different from a previous request
            # 0 for subcase means that its not necessary to add forces data as the request is coords or id
            if subcase_id not in (0, self.last_subcase_id):
                subcase = self.subcases[subcase_id]
                node_id2forces = subcase.node_id2forces
                for node_id, forces in node_id2forces.items():
                    node = session.exec(
                        select(NodeDBModel).filter(NodeDBModel.id == node_id)
                    ).first()
                    node.fx = forces[0]
                    node.fy = forces[1]
                    node.fz = forces[2]
                    node.fabs = (
                        forces[0] ** 2 + forces[1] ** 2 + forces[2] ** 2
                    ) ** 0.5
                    node.mx = forces[3]
                    node.my = forces[4]
                    node.mz = forces[5]
                    node.mabs = (
                        forces[3] ** 2 + forces[4] ** 2 + forces[5] ** 2
                    ) ** 0.5
            self.last_subcase_id = subcase_id
            session.commit()

            # Apply sorting based on the specified column and direction
            if sort_direction == 1:
                query = query.order_by(asc(getattr(NodeDBModel, sort_column)))
            elif sort_direction == -1:
                query = query.order_by(desc(getattr(NodeDBModel, sort_column)))

            # caching for speed
            self.last_query = query
            self.last_sort_column = sort_column
            self.last_sort_direction = sort_direction
            self.last_filter = node_ids

            # Execute the query and return the results (with pagination)
            return session.exec(query.offset(offset).limit(limit)).all()

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
