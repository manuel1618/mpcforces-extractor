import unittest
from unittest.mock import patch
from mpcforces_extractor.force_extractor import MPCForceExtractor, FEMExtractor
from mpcforces_extractor.reader.modelreaders import FemFileReader
from mpcforces_extractor.datastructure.entities import Element, Part
from mpcforces_extractor.visualization.tcl_visualize import VisualizerConnectedParts
from mpcforces_extractor.datastructure.subcases import Subcase
from mpcforces_extractor.datastructure.rigids import MPC
from mpcforces_extractor.test_ressources.simple_model import (
    get_simple_model_fem,
    get_simple_model_mpc,
)
from mpcforces_extractor.datastructure.rigids import MPC_CONFIG


class TestFMPCForceExtractor(unittest.TestCase):
    def test_init(self):
        """
        Test the init method. Make sure all variables are set correctly (correct type)
        """
        # reset instances
        Element.reset_graph()
        Part.reset()
        Subcase.reset()

        # Test the init method
        force_extractor = MPCForceExtractor(
            mpcf_file_path="test.mpcf",
        )
        self.assertEqual(force_extractor.mpcf_file_path, "test.mpcf")

    @patch(
        "mpcforces_extractor.force_extractor.MPCForceExtractor._MPCForceExtractor__mpcf_file_exists"
    )
    @patch(
        "mpcforces_extractor.reader.modelreaders.FemFileReader._FemFileReader__read_lines"
    )
    @patch(
        "mpcforces_extractor.reader.forces_reader.ForcesReader._ForcesReader__read_lines"
    )
    def test_extract_forces_and_summary(
        self, mock_read_lines_mpc, mock_read_lines_fem, mock_mpcf_file_exists
    ):
        """
        Test the extract_forces method. Make sure the forces are extracted correctly
        """

        mock_read_lines_fem.return_value = get_simple_model_fem()
        mock_read_lines_mpc.return_value = get_simple_model_mpc()
        mock_mpcf_file_exists.return_value = True

        # reset instances
        Element.reset_graph()
        Part.reset()
        Subcase.reset()
        MPC.reset()

        # Test the extract_forces method
        fem_extractor = FEMExtractor(None, 8)
        fem_extractor.build_fem_data()
        force_extractor = MPCForceExtractor(mpcf_file_path="test.mpcf")
        force_extractor.build_subcase_data()

        force_1 = [0.00, 0.00, -1.00, -0.91, 0.00, 0.00]
        force_2 = [0.00, 0.00, 1.00, 1.32, 5.84, 1.94]

        for subcase in Subcase.subcases:
            RBE2CONFIG = MPC_CONFIG.RBE2.value
            part_id2forces = list(MPC.config_2_id_2_instance[RBE2CONFIG].values())[
                0
            ].get_part_id2force(subcase)
            force_calc_1 = part_id2forces[1]
            force_calc_2 = part_id2forces[2]

            diff_1 = sum([abs(a_i - b_i) for a_i, b_i in zip(force_1, force_calc_1)])
            diff_2 = sum([abs(a_i - b_i) for a_i, b_i in zip(force_2, force_calc_2)])
            self.assertTrue(diff_1 < 0.01 or diff_2 < 0.01)

    @patch(
        "mpcforces_extractor.reader.modelreaders.FemFileReader._FemFileReader__read_lines"
    )
    def test_extract_forces_non_mpcf_file(self, mock_read_lines_fem):
        """
        Test the extract_forces method. Make sure the forces are extracted correctly
        """

        mock_read_lines_fem.return_value = get_simple_model_fem()

        # reset instances
        Element.reset_graph()
        Part.reset()
        Subcase.reset()

        # Test the extract_forces method
        force_extractor = MPCForceExtractor(
            mpcf_file_path="none",
        )
        force_extractor.build_subcase_data()

        assert len(Subcase.subcases) == 0

    @patch(
        "mpcforces_extractor.reader.modelreaders.FemFileReader._FemFileReader__read_lines"
    )
    def test_visualize_tcl_commands(self, mock_read_lines_fem):

        mock_read_lines_fem.return_value = get_simple_model_fem()

        # reset instances
        Element.reset_graph()
        Part.reset()

        reader = FemFileReader(None, 8)
        reader.create_entities()

        # Visualize
        part_id2connected_node_ids = Element.get_part_id2node_ids_graph()
        self.assertTrue(part_id2connected_node_ids is not None)
        self.assertTrue(len(part_id2connected_node_ids) == 2)

        visualizer = VisualizerConnectedParts(None)
        visualizer.output_tcl_lines_for_part_vis()

        commands = visualizer.commands
        self.assertTrue(len(commands) == 6)

        commands_expected = []
        commands_expected.append("*createentity comps name=part1")
        commands_expected.append("*createmark elements 1 1 2 3 4")
        commands_expected.append('*movemark elements 1 "part1"')
        commands_expected.append("*createentity comps name=part2")
        commands_expected.append("*createmark elements 1 5 6 7 8")
        commands_expected.append('*movemark elements 1 "part2"')

        for _, command in enumerate(commands):
            self.assertTrue(command in commands_expected)


if __name__ == "__main__":
    unittest.main()
