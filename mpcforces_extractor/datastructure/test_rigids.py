import unittest
from mpcforces_extractor.datastructure.rigids import MPC, MPC_CONFIG
from mpcforces_extractor.datastructure.entities import Node
from mpcforces_extractor.datastructure.subcases import Subcase


class TestRigids(unittest.TestCase):
    def test_init(self):
        """
        Test the init method. Make sure all variables are set correctly (correct type)
        """

        # Test the init method
        mpc = MPC(
            element_id=1,
            mpc_config=MPC_CONFIG.RBE2,
            master_node=0,
            nodes=[1, 2],
            dofs="123",
        )
        self.assertEqual(mpc.element_id, 1)
        self.assertEqual(mpc.nodes, [1, 2])
        self.assertEqual(mpc.dofs, "123")

    def test_sum_forces_by_connected_parts(self):
        node_id2force = {
            1: [1, 1, 1, 0, 0, 0],
            2: [2, 2, 2, 0, 0, 0],
        }

        node1 = Node(
            node_id=1,
            coords=[0, 0, 0],
        )
        node2 = Node(
            node_id=2,
            coords=[0, 0, 0],
        )

        mpc = MPC(
            element_id=10,
            mpc_config=MPC_CONFIG.RBE2,
            master_node=0,
            nodes=[node1, node2],
            dofs="123",
        )

        subcase = Subcase(1, 1)
        subcase.node_id2forces = node_id2force

        forces = mpc.get_part_id2force(subcase)

        self.assertTrue(forces[1] == [3, 3, 3, 0, 0, 0])
