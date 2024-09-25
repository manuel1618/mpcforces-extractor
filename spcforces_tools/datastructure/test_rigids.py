import unittest
from spcforces_tools.datastructure.rigids import MPC, MPC_CONFIG


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
