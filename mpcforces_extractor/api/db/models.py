from typing import Dict
from sqlmodel import SQLModel, Field, Column, JSON


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


class NodeDBModel(SQLModel, table=True):
    """
    Database Representation of Node Instance
    """

    id: int = Field(primary_key=True)
    coord_x: float = Field()
    coord_y: float = Field()
    coord_z: float = Field()


class SubcaseDBModel(SQLModel, table=True):
    """
    Database Representation of Subcase Class
    """

    id: int = Field(primary_key=True)
    node_id2forces: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    time: float = Field()
