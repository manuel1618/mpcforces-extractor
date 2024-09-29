import unittest
from mpcforces_extractor.force_extractor import MPCForceExtractor


class TestFMPCForceExtractor(unittest.TestCase):

    def test_init(self):
        """
        Test the init method. Make sure all variables are set correctly (correct type)
        """

        # Test the init method
        force_extractor = MPCForceExtractor(
            fem_file_path="test.fem",
            mpc_file_path="test.mpc",
            output_folder="test",
        )
        self.assertEqual(force_extractor.fem_file_path, "test.fem")
        self.assertEqual(force_extractor.mpc_file_path, "test.mpc")
        self.assertEqual(force_extractor.output_folder, "test")

    def test_extract_forces(self):
        """
        Test the extract_forces method. Make sure the forces are extracted correctly
        """

        # Test the extract_forces method
        force_extractor = MPCForceExtractor(
            fem_file_path="test.fem",
            mpc_file_path="test.mpc",
            output_folder="test",
        )
        blocksize = 9
        forces = force_extractor.get_mpc_forces(blocksize)
        force_extractor.write_suammry(forces)
        force_extractor.write_tcl_vis_lines()
        self.assertEqual(forces, {})
