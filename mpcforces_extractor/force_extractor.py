import os
import time
from typing import Dict
from mpcforces_extractor.reader.modelreaders import FemFileReader
from mpcforces_extractor.reader.mpcforces_reader import MPCForcesReader
from mpcforces_extractor.datastructure.entities import Element


class MPCForceExtractor:
    """
    This class is used to extract the forces from the MPC forces file
    and calculate the forces for each rigid element by property
    """

    def __init__(self, fem_file_path, mpc_file_path, output_folder: str):
        self.fem_file_path: str = fem_file_path
        self.mpc_file_path: str = mpc_file_path
        self.output_folder: str = output_folder
        self.reader: FemFileReader = None
        self.part_id2connected_node_ids: Dict = {}
        self.node_id2forces = {}
        # reset the graph (very important)
        Element.reset_graph()

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

    def get_mpc_forces(self, block_size: int) -> dict:
        """
        This method reads the FEM File and the MPCF file and extracts the forces
        in a dictory with the rigid element as the key and the property2forces dict as the value
        """
        self.node_id2forces = MPCForcesReader(self.mpc_file_path).get_nodes2forces()
        self.reader = FemFileReader(self.fem_file_path, block_size)
        print("Reading the FEM file")
        start_time = time.time()
        self.reader.create_entities()

        print("..took ", round(time.time() - start_time, 2), "seconds")
        print("Building the mpcs")
        start_time = time.time()
        self.reader.get_rigid_elements()
        print("..took ", round(time.time() - start_time, 2), "seconds")

        self.reader.get_loads()
        # Element.get_neighbors()

        mpc2forces = {}

        # Get the connected Nodes for all nodes
        self.part_id2connected_node_ids = Element.get_part_id2node_ids_graph()

        for mpc in self.reader.rigid_elements:
            part_id2forces = mpc.sum_forces_by_connected_parts(
                self.node_id2forces, self.part_id2connected_node_ids
            )
            mpc2forces[mpc] = part_id2forces

            part_id2node_ids = mpc.part_id2node_ids
            # write it to the file
            file_path_out = os.path.join(
                self.output_folder, f"RigidElement_{mpc.element_id}.txt"
            )
            with open(file_path_out, "w", encoding="utf-8") as file:
                file.write(f"MPC Element ID: {mpc.element_id}\n")
                file.write(f"  MPC Config: {mpc.mpc_config}\n")
                master_node = mpc.master_node
                if master_node.id in self.node_id2forces:
                    forces = self.node_id2forces[master_node.id]
                    file.write(
                        f"  Master Node ID: {master_node.id}, Forces: {forces}\n"
                    )
                else:
                    file.write(f"  Master Node ID: {master_node.id}\n")
                file.write(f"  Master Node Coords: {master_node.coords}\n")

                file.write(f"  Slave Nodes: {len(mpc.nodes)}\n")
                file.write(f"  Parts: {len(part_id2node_ids)}\n")
                for part_id in sorted(part_id2node_ids.keys()):
                    node_ids = part_id2node_ids[part_id]
                    file.write(f"  Part ID: {part_id}\n")

                    file.write(f"    Slave Nodes: {len(node_ids)}\n")
                    node_ids_str = ", ".join([str(node_id) for node_id in node_ids])
                    file.write(f"    {node_ids_str}\n")

        return mpc2forces
