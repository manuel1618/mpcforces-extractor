import os
from typing import Dict
from mpcforces_extractor.datastructure.entities import Element


class VisualizerConnectedParts:
    """
    This class is used to visualize the connected parts in Hypermesh
    """

    def __init__(self, part_id2connected_node_ids: Dict, output_folder: str):
        """
        This class is used to visualize the connected parts in Hypermesh
        """
        self.part_id2connected_node_ids = part_id2connected_node_ids
        self.output_folder = output_folder
        self.part_id2connected_element_ids = {}
        self.commands = []

        # create output folder if it does not exist, otherwise delete the content
        if os.path.exists(output_folder):
            for file in os.listdir(output_folder):
                file_path = os.path.join(output_folder, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
        else:
            os.makedirs(output_folder, exist_ok=True)

    def __transform_nodes_to_elements(self):
        """
        This method transforms the connected nodes to connected elementsm
        """
        node_id2part_id = {}
        self.part_id2connected_element_ids = {}

        for part_id, connected_node_ids in self.part_id2connected_node_ids.items():
            for node_id in connected_node_ids:
                node_id2part_id[node_id] = part_id

        for _, element in Element.element_id2element.items():
            node = element.nodes[0]
            node_id = node.id
            part_id = node_id2part_id.get(node_id)
            if part_id is not None:
                if part_id not in self.part_id2connected_element_ids:
                    self.part_id2connected_element_ids[part_id] = []
                self.part_id2connected_element_ids[part_id].append(element.id)
            else:
                print(f"Node {node_id} not in node_id2part")

    def output_tcl_lines_for_part_vis(self):
        """
        Creates the tcl code for visualizing the connected parts
        in Hypermesh
        """
        if not self.part_id2connected_element_ids:
            self.__transform_nodes_to_elements()

        for (
            part_id,
            connected_element_ids,
        ) in self.part_id2connected_element_ids.items():
            self.commands.append(f"*createentity comps name=part{part_id}")

            # mark and move blocks of max 1000 elements
            self.commands.append(
                f"*createmark elements 1 {' '.join([str(i) for i in connected_element_ids])}"
            )
            self.commands.append(f'*movemark elements 1 "part{part_id}"')

        with open(
            os.path.join(self.output_folder, "commands.tcl"), "w", encoding="utf-8"
        ) as file:
            file.write("\n".join(self.commands))
