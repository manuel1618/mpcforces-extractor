import unittest
from spcforces_tools.datastructure.rigids import MPC


class TestRigids(unittest.TestCase):
    def test_init(self):
        """
        Test the init method. Make sure all variables are set correctly (correct type)
        """

        # Test the init method
        mpc = MPC(1, 0, [1, 2], "123")
        self.assertEqual(mpc.element_id, 1)
        self.assertEqual(mpc.nodes, [1, 2])
        self.assertEqual(mpc.dofs, "123")
        self.assertEqual(mpc.property2nodes, {})

    def test_sum_forces_by_property(self):
        """
        Test the sum_forces_by_property method. Make sure the forces are summed correctly
        """

        # Test the sum_forces_by_property method
        mpc = MPC(1, 0, [1, 2], "123")
        node2force = {1: [500, 0, 0, 0, 0, 0], 2: [-500, 0, 0, 0, 0, 0]}
        forces = mpc.sum_forces_by_property(node2force)
        self.assertEqual(forces, {})

        mpc.property2nodes = {1: [1], 2: [2], 3: [3]}
        forces = mpc.sum_forces_by_property(node2force)
        self.assertEqual(
            forces,
            {1: [500, 0, 0, 0, 0, 0], 2: [-500, 0, 0, 0, 0, 0], 3: [0, 0, 0, 0, 0, 0]},
        )

    def test_sort_nodes_by_property(self):
        """
        Test the sort_nodes_by_property method. Make sure the nodes are sorted correctly
        """

        # Test the sort_nodes_by_property method
        mpc = MPC(1, 0, [1, 2], "123")
        node2property = {1: 1, 2: 2, 3: 3}
        mpc.sort_nodes_by_property(node2property)
        self.assertEqual(mpc.property2nodes, {1: [1], 2: [2]})

        mpc = MPC(1, 0, [1, 2, 3], "123")
        node2property = {1: 1, 2: 2, 3: 1}
        mpc.sort_nodes_by_property(node2property)
        self.assertEqual(mpc.property2nodes, {1: [1, 3], 2: [2]})
