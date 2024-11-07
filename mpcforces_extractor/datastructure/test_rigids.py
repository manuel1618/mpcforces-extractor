import unittest
from mpcforces_extractor.datastructure.rigids import MPC, MPC_CONFIG
from mpcforces_extractor.datastructure.entities import Node, Element
from mpcforces_extractor.datastructure.subcases import Subcase


class TestRigids(unittest.TestCase):
    def test_init(self):
        """
        Test the init method. Make sure all variables are set correctly (correct type)
        """

        Node.reset()
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
        node_id2force = {
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
        Element(1, 1, [node1, node2, node3, node4])

        mpc = MPC(
            element_id=10,
            mpc_config=MPC_CONFIG.RBE2,
            master_node=node0,
            nodes=[node1, node2],
            dofs="123",
        )

        subcase = Subcase(1, 1)
        subcase.node_id2forces = node_id2force

        forces = mpc.get_part_id2force(subcase)
        self.assertTrue(forces[1] == [3, 3, 3, 0, 0, 0])


if __name__ == "__main__":
    unittest.main()
