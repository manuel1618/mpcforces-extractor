import unittest
from unittest.mock import patch

from mpcforces_tools.reader.mpcforces_reader import MPCForcesReader


@patch(
    "mpcforces_tools.reader.mpcforces_reader.MPCForcesReader._MPCForcesReader__read_lines"
)
class TestMPCForcesReader(unittest.TestCase):
    def test_get_nodes2forces(self, mock_read_lines):
        mpc_file_path = "dummypath"
        mock_read_lines.return_value = [
            "GRID #   X-FORCE      Y-FORCE      Z-FORCE      X-MOMENT     Y-MOMENT     Z-MOMENT\n",
            "--------+-----------------------------------------------------------------------------\n",
            "       1 -1.00000E-00  1.00000E-00  1.00000E-00  1.00000E-00\n",
            "       2 -1.00000E-00  1.00000E-00  1.00000E-00               1.00000E-00\n",
            "",
        ]

        mpc_reader = MPCForcesReader(mpc_file_path)
        mpc_reader.file_content = mock_read_lines.return_value

        nodes2forces = mpc_reader.get_nodes2forces()
        self.assertEqual(len(nodes2forces), 2)
        self.assertEqual(nodes2forces[1], [-1.0, 1.0, 1.0, 1.0, 0.0, 0.0])
        self.assertEqual(nodes2forces[2], [-1.0, 1.0, 1.0, 0.0, 1.0, 0.0])
