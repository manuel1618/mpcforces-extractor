import unittest
from unittest.mock import Mock, patch
import numpy as np
from mpcforces_extractor.datastructure.rigids import MPC, MPC_CONFIG
from mpcforces_extractor.datastructure.entities import Node, Element, Part
from mpcforces_extractor.datastructure.subcases import Subcase


class TestRigids(unittest.TestCase):
    def test_init(self):
        """
        Test the init method. Make sure all variables are set correctly (correct type)
        """

        Node.reset()
        MPC.reset()
        Element.reset_graph()
        node1 = Node(
            node_id=1,
            coords=[0, 0, 0],
        )
        node2 = Node(
            node_id=2,
            coords=[0, 0, 0],
        )

        # Test the init method
        mpc = MPC(
            element_id=1,
            mpc_config=MPC_CONFIG.RBE2,
            master_node=node1,
            nodes=[node2],
            dofs="123",
        )
        self.assertEqual(mpc.element_id, 1)
        self.assertEqual(mpc.nodes, [node2])
        self.assertEqual(mpc.master_node, node1)
        self.assertEqual(mpc.dofs, "123")

    def test_sum_forces_by_connected_parts(self):
        node_id2mpcforce = {
            1: [1, 1, 1, 0, 0, 0],
            2: [2, 2, 2, 0, 0, 0],
        }
        node0 = Node(
            node_id=0,
            coords=[0, 0, 0],
        )

        node1 = Node(
            node_id=1,
            coords=[0, 0, 0],
        )
        node2 = Node(
            node_id=2,
            coords=[0, 0, 0],
        )
        node3 = Node(
            node_id=3,
            coords=[0, 0, 0],
        )
        node4 = Node(
            node_id=4,
            coords=[0, 0, 0],
        )
        Element.reset_graph()
        Part.reset()
        Element(1, 1, [node1, node2, node3, node4])

        mpc = MPC(
            element_id=10,
            mpc_config=MPC_CONFIG.RBE2,
            master_node=node0,
            nodes=[node1, node2],
            dofs="123",
        )

        subcase = Subcase(1, 1)
        subcase.node_id2mpcforces = node_id2mpcforce

        forces = mpc.get_part_id2force(subcase)
        self.assertTrue(forces[1] == [3, 3, 3, 0, 0, 0])


class TestMPCMethods(unittest.TestCase):
    def setUp(self):
        # Mocked nodes
        Element.reset_graph()
        Node.reset()
        MPC.reset()

        self.master_node = Mock(spec=Node, coords=[0.0, 0.0, 0.0], id=0)
        self.slave_nodes = [
            Mock(spec=Node, coords=[1.0, 0.0, 0.0], id=1),
            Mock(spec=Node, coords=[0.0, 1.0, 0.0], id=2),
            Mock(spec=Node, coords=[0.0, 0.0, 1.0], id=3),
        ]

        # Create MPC instance
        self.mpc = MPC(
            element_id=1,
            mpc_config=MPC_CONFIG.RBE2,
            master_node=self.master_node,
            nodes=self.slave_nodes,
            dofs="123",
        )

    def test_compute_axis(self):
        axis = self.mpc._MPC__fit_axis_for_cylindrical()

        # Validate axis
        np.testing.assert_almost_equal(
            axis, [0.57735027, 0.57735027, 0.57735027], decimal=6
        )

    @patch("mpcforces_extractor.datastructure.rigids.MPC.get_part_id2force")
    @patch("mpcforces_extractor.datastructure.subcases.Subcase.get_sum_forces")
    @patch(
        "mpcforces_extractor.datastructure.entities.Element.get_part_id2node_ids_graph"
    )
    def test_get_part_id2axial_radial_forces(
        self,
        mock_get_part_id2node_ids_graph,
        mock_get_sum_forces,
        mock_get_part_id2force,
    ):
        # Mock dependencies
        mock_get_part_id2node_ids_graph.return_value = {
            1: [node.id for node in self.slave_nodes]
        }
        mock_get_sum_forces.return_value = [1.0, 2.0, 3.0]  # Example forces
        mock_get_part_id2force.return_value = {1: [1.0, 2.0, 3.0]}

        # Mock subcase
        subcase = Mock(spec=Subcase)

        # Test method
        part_id2axial_radial_forces = self.mpc.get_part_id2axial_radial_forces(subcase)

        # Expected results
        axis = np.array(self.mpc.axis)
        forces = np.array([1.0, 2.0, 3.0])
        axial_force = np.dot(forces, axis) * axis
        radial_force = forces - axial_force

        self.assertIn(1, part_id2axial_radial_forces)
        np.testing.assert_almost_equal(
            part_id2axial_radial_forces[1]["axial_force"],
            axial_force.tolist(),
            decimal=6,
        )
        np.testing.assert_almost_equal(
            part_id2axial_radial_forces[1]["radial_force"],
            radial_force.tolist(),
            decimal=6,
        )

    def test_get_shear_stress(self):
        self.mpc.diameter = 2.0  # Set a known diameter
        max_radial_force = 10.0  # Example force
        max_axial_force = 5.0  # Example force

        shear_stress, norm_stress = self.mpc.get_shear_and_axial_stress(
            max_radial_force, max_axial_force
        )

        # Area = pi * r^2 = pi * (diameter / 2)^2
        expected_area = np.pi * (2.0 / 2) ** 2
        expected_shear_stress = max_radial_force / expected_area
        expected_norm_stress = max_axial_force / expected_area

        self.assertAlmostEqual(shear_stress, expected_shear_stress, places=6)
        self.assertAlmostEqual(norm_stress, expected_norm_stress, places=6)

    def test_get_max_radial_axial_force(self):
        # Mock Subcases
        subcase1 = Mock(spec=Subcase)
        subcase2 = Mock(spec=Subcase)

        Subcase.subcases = [subcase1, subcase2]

        # Mock get_part_id2axial_radial_forces for each subcase
        self.mpc.get_part_id2axial_radial_forces = Mock(
            side_effect=[
                {
                    1: {"axial_force": [1.0, 0.0, 0.0], "radial_force": [3.0, 4.0, 0.0]}
                },  # Subcase 1
                {
                    2: {"axial_force": [0.0, 0.0, 0.0], "radial_force": [6.0, 8.0, 0.0]}
                },  # Subcase 2
            ]
        )

        # Test get_max_radial_and_axial_force
        (
            max_subcase,
            max_part_id,
            max_radial_force,
            max_ax_subcase,
            max_ax_part,
            max_ax_stress,
        ) = self.mpc.get_max_radial_and_axial_force()

        # Validate results
        self.assertEqual(max_subcase, subcase2)
        self.assertEqual(max_part_id, 2)
        self.assertAlmostEqual(max_radial_force, 10.0, places=6)

        self.assertEqual(max_ax_subcase, subcase1)
        self.assertEqual(max_ax_part, 1)
        self.assertAlmostEqual(max_ax_stress, 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
