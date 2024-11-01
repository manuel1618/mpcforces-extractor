from typing import Dict
from sqlmodel import SQLModel, Field, Column, JSON
from mpcforces_extractor.datastructure.rigids import MPC, MPC_CONFIG
from mpcforces_extractor.datastructure.entities import Node
from mpcforces_extractor.datastructure.subcases import Subcase


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
    subcase_id2part_id2forces: Dict = Field(
        default_factory=dict, sa_column=Column(JSON)
    )  # Store subcase_id2part_id2forces as a dictionary

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


class SubcaseDBModel(SQLModel, table=True):
    """
    Database Representation of Subcase Class
    """

    id: int = Field(primary_key=True)
    node_id2forces: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    time: float = Field()

    def to_subcase(self):
        """
        Method to convert SubcaseDBModel back to Subcase object if needed
        """
        subcase = Subcase(subcase_id=self.id, time=self.time)
        for node_id, forces in self.node_id2forces.items():
            subcase.add_force(node_id, forces)
        return subcase
