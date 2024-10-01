import unittest
from unittest.mock import patch
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

    @patch(
        "mpcforces_extractor.reader.mpcforces_reader.MPCForcesReader._MPCForcesReader__read_lines"
    )
    @patch(
        "mpcforces_extractor.reader.modelreaders.FemFileReader._FemFileReader__read_lines"
    )
    def test_extract_forces(self, mock_read_lines_mpc, mock_read_lines_fem):
        """
        Test the extract_forces method. Make sure the forces are extracted correctly
        """

        mock_read_lines_fem.return_value = ["1"]
        mock_read_lines_mpc.return_value = ["1"]

        # Test the extract_forces method
        force_extractor = MPCForceExtractor(
            fem_file_path="test.fem",
            mpc_file_path="test.mpc",
            output_folder="test",
        )
        blocksize = 8
        forces = force_extractor.get_mpc_forces(blocksize)
        self.assertEqual(forces, {})


if __name__ == "__main__":
    unittest.main()
