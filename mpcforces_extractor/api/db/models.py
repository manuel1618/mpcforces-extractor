from typing import Dict
from sqlmodel import SQLModel, Field, Column, JSON


class RBE3DBModel(SQLModel, table=True):
    """
    Database Representation of RBE3 Class
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


class RBE2DBModel(SQLModel, table=True):
    """
    Database Representation of RBE2 Class
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
    fx: float = Field(default=0.0)
    fy: float = Field(default=0.0)
    fz: float = Field(default=0.0)
    fabs: float = Field(default=0.0)
    mx: float = Field(default=0.0)
    my: float = Field(default=0.0)
    mz: float = Field(default=0.0)
    mabs: float = Field(default=0.0)


class SubcaseDBModel(SQLModel, table=True):
    """
    Database Representation of Subcase Class
    """

    id: int = Field(primary_key=True)
    node_id2forces: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    time: float = Field()
