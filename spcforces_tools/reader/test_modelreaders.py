import unittest
from unittest.mock import patch
from spcforces_tools.reader.modelreaders import FemFileReader
from spcforces_tools.datastructure.entities import Node


class TestFemFileReader(unittest.TestCase):

    # the __read_lines method is a private method, so we need to mock it and return propper file_content
    @patch(
        "spcforces_tools.reader.modelreaders.FemFileReader._FemFileReader__read_lines"
    )
    def test_init(self, mock_read_lines):
        """
        Test the init method. Make sure all variables are set correctly (correct type)
        """

        # Test the init method
        mock_read_lines.return_value = []
        fem_file_reader = FemFileReader("test.fem", 8)
        self.assertEqual(fem_file_reader.file_path, "test.fem")
        self.assertEqual(fem_file_reader.nodes_id2node, {})
        self.assertEqual(fem_file_reader.rigid_elements, [])
        self.assertEqual(fem_file_reader.node2property, {})
        self.assertEqual(fem_file_reader.blocksize, 8)

    @patch(
        "spcforces_tools.reader.modelreaders.FemFileReader._FemFileReader__read_lines"
    )
    @patch(
        "spcforces_tools.reader.modelreaders.FemFileReader._FemFileReader__read_nodes"
    )
    def test_split_line(self, mock_read_lines, mock_read_nodes):
        """
        Test the split_line method. Make sure the line is split correctly
        """
        mock_read_lines.return_value = []
        mock_read_nodes.return_value = []
        # Test the split_line method
        fem_file_reader = FemFileReader("test.fem", 8)
        line = "1234567890"
        line_content = fem_file_reader.split_line(line)
        self.assertEqual(line_content, ["12345678", "90"])

        line = "123456789"
        line_content = fem_file_reader.split_line(line)
        self.assertEqual(line_content, ["12345678", "9"])

    @patch(
        "spcforces_tools.reader.modelreaders.FemFileReader._FemFileReader__read_lines"
    )
    @patch(
        "spcforces_tools.reader.modelreaders.FemFileReader._FemFileReader__read_nodes"
    )
    def test_bulid_node2property(self, mock_read_lines, mock_read_nodes):
        """
        Test the bulid_node2property method. Make sure the node2property is built correctly
        """
        mock_read_lines.return_value = [
            "GRID           1        -16.889186.0    13.11648\n",
            "CHEXA        497       1       1       2       3\n",
            "+              4       5\n",
            "RBE2           1       2  123456       3       4       5       6       7\n",
        ]

        mock_read_nodes.return_value = {1: [0.0, 0.0, 0.0], 2: [0.0, 0.0, 0.0]}

        fem_file_reader = FemFileReader("test.fem", 8)
        fem_file_reader.file_content = mock_read_lines.return_value

        fem_file_reader.bulid_node2property()
        self.assertEqual(fem_file_reader.node2property, {1: 1, 2: 1, 3: 1, 4: 1, 5: 1})

    @patch(
        "spcforces_tools.reader.modelreaders.FemFileReader._FemFileReader__read_lines"
    )
    @patch(
        "spcforces_tools.reader.modelreaders.FemFileReader._FemFileReader__read_nodes"
    )
    def test_get_rigid_elements(self, mock_read_lines, mock_read_nodes):
        """
        Test the get_rigid_elements method. Make sure the rigid elements are extracted correctly
        """
        mock_read_lines.return_value = [
            "GRID           1        -16.889186.0    13.11648\n",
            "GRID           2        -0.0    0.0     0.0     \n",
            "CHEXA        497       1       1       2       3\n",
            "+              4       5\n",
            "RBE2           1       2  123456       3       4       5       6       7\n",
            "+              8\n",
            "\n",
        ]
        mock_read_nodes.return_value = {
            1: Node(1, [-16.8891, 86.0, 13.11648]),
            2: Node(2, [0.0, 0.0, 0.0]),
        }

        fem_file_reader = FemFileReader("test.fem", 8)
        fem_file_reader.file_content = mock_read_lines.return_value
        fem_file_reader.nodes_id2node = mock_read_nodes.return_value

        fem_file_reader.get_rigid_elements()

        # dont care about the order of the dict
        self.assertEqual(
            fem_file_reader.rigid_elements[0].element_id, 1
        )  # check the element_id
        self.assertEqual(
            fem_file_reader.rigid_elements[0].dofs, 123456
        )  # check the dofs
        self.assertEqual(
            fem_file_reader.rigid_elements[0].nodes, [3, 4, 5, 6, 7, 8]
        )  # check the nodes

        self.assertEqual(
            fem_file_reader.rigid_elements[0].master_node.id, 2
        )  # check the master_node
        self.assertEqual(
            fem_file_reader.rigid_elements[0].master_node.coords, [0.0, 0.0, 0.0]
        )


if __name__ == "__main__":
    unittest.main()
