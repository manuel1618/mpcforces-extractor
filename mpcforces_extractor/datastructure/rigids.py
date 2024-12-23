from typing import Dict, List
from enum import Enum
import numpy as np
from mpcforces_extractor.datastructure.entities import Node, Element
from mpcforces_extractor.datastructure.subcases import Subcase, ForceType
from mpcforces_extractor.util.logger import Logger


class MPC_CONFIG(Enum):
    """
    Enum to represent the MPC configuration
    """

    RBE2 = 1
    RBE3 = 2


class MPC:
    """
    This class is a Multiple Point Constraint (MPC) class that is used to store the nodes and the dofs
    """

    config_2_id_2_instance: Dict[int, "MPC"] = {}
    all_instances: List["MPC"] = []

    def __init__(
        self,
        *,  # fixes the too many positional arguments error from the linter by forcing the use of keyword arguments
        element_id: int,
        mpc_config: MPC_CONFIG,
        master_node: Node,
        nodes: List,
        dofs: str,
    ):
        self.element_id: int = element_id
        self.mpc_config: MPC_CONFIG = mpc_config
        if master_node is None:
            Logger().log_warn("Master_node2coords is None for element_id", element_id)
        self.master_node: Node = master_node
        self.nodes: List = nodes
        self.dofs: int = dofs
        self.part_id2node_ids = {}
        self.axis = None

        # config_2_id_2_instance
        if mpc_config.value not in MPC.config_2_id_2_instance:
            MPC.config_2_id_2_instance[mpc_config.value] = {}
        if element_id in MPC.config_2_id_2_instance[mpc_config.value]:
            Logger().log_err(
                f"Element with id {element_id} already exists for config {mpc_config}"
            )
        MPC.config_2_id_2_instance[mpc_config.value][element_id] = self
        MPC.all_instances.append(self)

    @staticmethod
    def reset():
        """
        This method is used to reset the instances
        """
        MPC.config_2_id_2_instance = {}

    def get_part_id2force(self, subcase: Subcase) -> Dict:
        """
        This method is used to get the forces for each part of the MPC (connected slave nodes)
        """

        if not self.part_id2node_ids:
            # Connected groups of nodes - get then the intersection with the slave nodes
            part_id2connected_node_ids = Element.get_part_id2node_ids_graph()
            part_id2node_ids = {}
            mpc_node_ids = [node.id for node in self.nodes]
            mpc_node_ids.append(self.master_node.id)
            for part_id, node_ids in part_id2connected_node_ids.items():
                part_id2node_ids[part_id] = list(
                    set(node_ids).intersection(mpc_node_ids)
                )

            self.part_id2node_ids = part_id2node_ids

        # Calculate the summed forces for each part
        part_id2forces = {}
        for part_id, node_ids in self.part_id2node_ids.items():
            sum_forces = [0, 0, 0]
            if subcase is not None:
                sum_forces = subcase.get_sum_forces(node_ids, ForceType.MPCFORCE)
            part_id2forces[part_id] = sum_forces
        return part_id2forces

    def get_subcase_id2part_id2force(self) -> Dict:
        """
        This method is used to get the forces for each part of the MPC (connected slave nodes)
        """

        subcase_id2part_id2forces = {}
        for subcase in Subcase.subcases:
            part_id2forces = self.get_part_id2force(subcase)
            subcase_id2part_id2forces[subcase.subcase_id] = part_id2forces
        return subcase_id2part_id2forces

    def __fit_axis_for_cylindrical(self) -> List[float]:
        """
        This method is used to fit the axis for cylindrical MPCs
        """
        if self.axis is not None:
            return self.axis

        point_cloud = np.array([node.coords for node in self.nodes])
        centroid = np.array(self.master_node.coords)
        shifted_points = point_cloud - centroid

        # Fit a cylinder axis using PCA (for simplicity)
        covariance_matrix = np.cov(shifted_points, rowvar=False)
        _, eigenvectors = np.linalg.eigh(covariance_matrix)
        axis = eigenvectors[:, -1]
        axis /= np.linalg.norm(axis)  # Normalize the axis

        # Save the axis
        self.axis = axis.tolist()
        return self.axis

    def get_part_id2axial_radial_forces(self, subcase: Subcase) -> Dict:
        """
        This method is used to get the axial and radial forces for the cylindrical MPCs
        """

        part_id2forces = self.get_part_id2force(subcase)
        number_of_parts = len(self.part_id2node_ids.keys())
        for part_id, nodes in self.part_id2node_ids.items():
            if len(nodes) == 0:
                number_of_parts -= 1
        if number_of_parts < 2:
            Logger().log_warn(
                f"Only one part connected to the MPC: {self.element_id}. Calc axial forces not implemented."
            )
            # maybe do that later with a tolerance value.
            # pca - max eigenvalue ... perpendicular... plane... all in tolerance ?
            # then axial = perpendicular to max eigenvalue eigenvector
            return {}

        if self.axis is None:
            self.axis = self.__fit_axis_for_cylindrical()

        # Convert axis to a NumPy array
        axis = np.array(self.axis)

        part_id2axial_radial_forces = {}
        for part_id, forces in part_id2forces.items():
            # Forces are in global coordinates; extract only the first 3 components, no moments
            forces = np.array(forces[0:3])

            # Compute axial force (projection onto the axis)
            axial_force_magnitude = np.dot(forces, axis)
            axial_force = axial_force_magnitude * axis

            # Compute radial force (remaining force perpendicular to the axis)
            radial_force = forces - axial_force

            # Store results
            part_id2axial_radial_forces[part_id] = {
                "axial_force": axial_force.tolist(),
                "radial_force": radial_force.tolist(),
                "axis": self.axis,
            }

        return part_id2axial_radial_forces
