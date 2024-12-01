from typing import List, Dict
import networkx as nx
from mpcforces_extractor.datastructure.entities import Node, Element
from mpcforces_extractor.datastructure.subcases import Subcase


class Moment:
    """
    Simple representation of a moment from the .fem file
    """

    def __init__(
        self,
        *,
        moment_id: int,
        node_id: int,
        system_id: int,
        scale_factor: float,
        compenents_from_file: List[str],
    ):
        self.id = moment_id
        self.node_id = node_id
        self.system_id = system_id
        self.compenents = [
            scale_factor * float(compenent) for compenent in compenents_from_file
        ]


class Force:
    """
    Simple representation of a force from the .fem file
    """

    def __init__(
        self,
        *,
        force_id: int,
        node_id: int,
        system_id: int,
        scale_factor: float,
        compenents_from_file: List[str],
    ):
        self.id = force_id
        self.node_id = node_id
        self.system_id = system_id
        self.compenents = [
            scale_factor * float(compenent) for compenent in compenents_from_file
        ]


class SPC:
    """
    Simple representation of a SPC from the .fem file (Single Point Constraint)
    """

    node_id_2_instance = {}

    def __init__(
        self,
        node_id: int,
        system_id: int,
        dofs: Dict[int, float],
    ):
        self.node_id = node_id
        self.system_id = system_id
        self.dofs = dofs
        if node_id in SPC.node_id_2_instance:
            print("Error: SPC already exists for node_id", node_id)
        SPC.node_id_2_instance[node_id] = self
        self.subcase_id2force = {}

    @staticmethod
    def reset():
        """
        Reset the SPC
        """
        SPC.node_id_2_instance = {}


class SPCCluster:
    """
    A collection of SPCs
    """

    id_2_instances = {}

    def __init__(self, spcs: List[SPC]):
        self.spcs = spcs
        self.id = len(SPCCluster.id_2_instances) + 1
        self.subcase_id2summed_force = {}
        SPCCluster.id_2_instances[self.id] = self

    def add_spcc(self, spcc: SPC):
        """
        Add a SPC to the cluster
        """
        self.spcs.append(spcc)

    @staticmethod
    def build_spc_cluster() -> None:
        """
        This method is used to build the SPC cluster
        """
        graph: nx.Graph = Element.graph.copy()
        all_spc_nodes = set()
        for node_id, _ in SPC.node_id_2_instance.items():
            all_spc_nodes.add(Node.node_id2node[node_id])
        spc_graph = graph.subgraph(all_spc_nodes)
        connected_components = list(nx.connected_components(spc_graph))
        for connected_component in connected_components:
            spcs = []
            for node in connected_component:
                spcs.append(SPC.node_id_2_instance[node.id])
            SPCCluster(spcs)

    @staticmethod
    def calculate_force_sum() -> None:
        """
        This method is used to calculate the sum of the spc forces
        for each subcase and for each spc cluster
        """
        # Calculate the sum of the forces for each spc cluster
        for _, spc_cluster in SPCCluster.id_2_instances.items():
            subcase_id2summed_force = {}
            for subcase in Subcase.subcases:
                node_id2forces = subcase.node_id2spcforces
                sum_forces = [0, 0, 0, 0, 0, 0]
                for spc in spc_cluster.spcs:
                    if spc.node_id not in node_id2forces:
                        print(f"Node {spc.node_id} not found in spcf, setting to 0.")
                        continue
                    force_vector = node_id2forces[spc.node_id]

                    # add the force to the SPC instance
                    spc.subcase_id2force[subcase.subcase_id] = force_vector

                    sum_forces = [sf + f for sf, f in zip(sum_forces, force_vector)]
                subcase_id2summed_force[subcase.subcase_id] = sum_forces
            spc_cluster.subcase_id2summed_force = subcase_id2summed_force

    @staticmethod
    def reset():
        """
        Reset the SPCCluster
        """
        SPCCluster.id_2_instances = {}
