import unittest
from unittest.mock import patch

from mpcforces_extractor.reader.forces_reader import ForcesReader
from mpcforces_extractor.datastructure.subcases import Subcase, ForceType


@patch(
    "mpcforces_extractor.reader.forces_reader.ForcesReader._ForcesReader__read_lines"
)
class TestForcesReader(unittest.TestCase):
    def test_forces(self, mock_read_lines):
        mpcf_file_path = "dummypath"
        mock_read_lines.return_value = [
            "$SUBCASE 1\n",
            "$TIME 0.0\n",
            "GRID #   X-FORCE      Y-FORCE      Z-FORCE      X-MOMENT     Y-MOMENT     Z-MOMENT\n",
            "--------+-----------------------------------------------------------------------------\n",
            "       1 -1.00000E-00  1.00000E-00  1.00000E-00  1.00000E-00\n",
            "       2 -1.00000E-00  1.00000E-00  1.00000E-00               1.00000E-00\n",
            "",
        ]

        # reset instances
        Subcase.reset()

        mpc_reader = ForcesReader(mpcf_file_path)
        mpc_reader.file_content = mock_read_lines.return_value
        mpc_reader.build_subcases(ForceType.MPCFORCE)

        self.assertEqual(len(Subcase.subcases), 1)
        subacase: Subcase = Subcase.subcases[0]
        self.assertEqual(
            subacase.node_id2mpcforces[1],
            [-1.0, 1.0, 1.0, 1.0, 0.0, 0.0],
        )
        self.assertEqual(
            Subcase.get_subcase_by_id(1).node_id2mpcforces[2],
            [-1.0, 1.0, 1.0, 0.0, 1.0, 0.0],
        )
