from typing import Dict, List, Tuple
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
        self.part_id2node_ids: Dict = {}
        self.axis: List[float] = None
        self.diameter: float = None
        self.length: float = None
        self.area: float = None

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
        This method is used to fit the axis for cylindrical MPCs.
        Dynamically determines the axis based on eigenvalue clustering.
        """
        if self.axis is not None:
            return self.axis

        point_cloud = np.array([node.coords for node in self.nodes])
        centroid = np.array(self.master_node.coords)
        shifted_points = (
            point_cloud - centroid
        )  # Center the points around the master node

        # PCA: Compute the covariance matrix and eigen decomposition
        covariance_matrix = np.cov(shifted_points, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

        # Check if all eigenvalues are too similar (potential for a flat or degenerate structure)
        if np.isclose(eigenvalues[0], eigenvalues[1], atol=1e-6) and np.isclose(
            eigenvalues[1], eigenvalues[2], atol=1e-6
        ):
            Logger().log_error(
                f"Element {self.element_id} has nearly identical eigenvalues {eigenvalues}; "
                f"cylinder axis is ambiguous."
            )
            raise ValueError(
                "Cylinder axis could not be determined; all eigenvalues are too similar."
            )

        # Identify the outlier eigenvalue
        mean_of_two_smallest = np.mean(sorted(eigenvalues)[:2])
        differences = [abs(ev - mean_of_two_smallest) for ev in eigenvalues]
        outlier_index = np.argmax(differences)

        # Select the eigenvector corresponding to the outlier eigenvalue
        axis = eigenvectors[:, outlier_index]

        # Handle degenerate cases (e.g., 2D plane of points)
        if np.isclose(
            sorted(eigenvalues)[0], 0, atol=1e-6
        ):  # Detect near-zero variance
            Logger().log_warn(
                f"Element {self.element_id} has a 2D plane of nodes; "
                f"axis will be the cross product of the two dominant eigenvectors"
            )
            zero_index = np.argmin(eigenvalues)
            # cross the other indices
            axis = np.cross(
                eigenvectors[:, (zero_index + 1) % 3],
                eigenvectors[:, (zero_index + 2) % 3],
            )

        axis /= np.linalg.norm(axis)  # Normalize the axis

        # Save and return the axis
        self.axis = axis.tolist()
        self.__compute_diameter_and_length(shifted_points, axis)

        return self.axis

    def __compute_diameter_and_length(
        self, shifted_points: np.array, axis: np.array
    ) -> None:
        """
        Calculates the diameter and length of the cylindrical MPC
        """
        # Project points onto the axis
        projections = np.dot(shifted_points, axis)

        # Compute length (range of projections along the axis)
        min_proj = np.min(projections)
        max_proj = np.max(projections)
        self.length = max_proj - min_proj

        # Compute distances from points to the axis
        distances = np.linalg.norm(shifted_points - np.outer(projections, axis), axis=1)
        self.diameter = 2 * np.max(distances)

    def get_part_id2axial_radial_forces(self, subcase: Subcase) -> Dict:
        """
        This method is used to get the axial and radial forces for the cylindrical MPCs
        """

        part_id2forces = self.get_part_id2force(subcase)

        if self.axis is None:
            self.axis = self.__fit_axis_for_cylindrical()

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
            }

        return part_id2axial_radial_forces

    def get_max_radial_force(self) -> Tuple[Subcase, int, float]:
        """
        This method gets the maximum radial force and the corresponding subcase and part id
        """
        max_radial_force = 0
        max_part_id = None
        max_subcase = None
        for subcase in Subcase.subcases:
            part_id2axial_radial_forces = self.get_part_id2axial_radial_forces(subcase)
            for part_id, forces in part_id2axial_radial_forces.items():
                radial_force = np.linalg.norm(forces["radial_force"])  # magnitude
                if radial_force > max_radial_force:
                    max_radial_force = radial_force
                    max_part_id = part_id
                    max_subcase = subcase

        return max_subcase, max_part_id, max_radial_force

    def get_shear_stress(self, max_radial_force: float) -> float:
        """
        This method is used to get the shear stress
        """

        if self.diameter is None:
            Logger().log_warn("Diameter is None for element_id", self.element_id)
            return 0
        self.area = np.pi * (self.diameter / 2) ** 2
        shear_stress = max_radial_force / self.area
        return shear_stress
