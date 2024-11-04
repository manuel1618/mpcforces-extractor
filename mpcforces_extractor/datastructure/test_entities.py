import unittest
from mpcforces_extractor.datastructure.entities import Element1D, Node, Element


class TestElement1D(unittest.TestCase):
    def test_init(self):
        """
        Test the init method. Make sure all variables are set correctly (correct type)
        """

        # Test the init method
        element = Element1D(
            element_id=1,
            property_id=1,
            node1=0,
            node2=1,
        )
        self.assertEqual(element.id, 1)
        self.assertEqual(element.property_id, 1)
        self.assertEqual(element.node1, 0)
        self.assertEqual(element.node2, 1)


class TestNode(unittest.TestCase):
    def test_init(self):
        """
        Test the init method. Make sure all variables are set correctly (correct type)
        """

        # Test the init method
        node = Node(
            node_id=1,
            coords=[0, 0, 0],
        )
        self.assertEqual(node.id, 1)
        self.assertEqual(node.coords, [0, 0, 0])

    def test_add_Element(self):
        """
        Test the add_element method. Make sure the element is added to the connected elements
        """

        # Test the add_element method
        node = Node(
            node_id=1,
            coords=[0, 0, 0],
        )
        element = Element1D(
            element_id=1,
            property_id=1,
            node1=0,
            node2=1,
        )
        node.add_element(element)
        self.assertEqual(node.connected_elements, [element])


class TestElement(unittest.TestCase):
    """
    Test the Element class
    """

    def test_init(self):
        """
        Test the init method. Make sure all variables are set correctly (correct type)
        """

        # Nodes
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
        nodes = [node1, node2, node3]

        # Test the init method
        element = Element(
            element_id=1,
            property_id=1,
            nodes=nodes,
        )
        self.assertEqual(element.id, 1)
        self.assertEqual(element.property_id, 1)
        self.assertEqual(element.nodes, nodes)
