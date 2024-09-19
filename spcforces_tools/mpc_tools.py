import os
import time
from spcforces_tools.reader.modelreaders import FemFileReader
from spcforces_tools.reader.mpcforces_reader import MPCForcesReader


class MPCForceExtractor:
    """
    This class is used to extract the forces from the MPC forces file
    and calculate the forces for each rigid element by property
    """

    def __init__(self, fem_file_path, mpc_file_path):
        self.fem_file_path = fem_file_path
        self.mpc_file_path = mpc_file_path

    def get_mpc_forces(self, block_size: int) -> dict:
        """
        This method reads the FEM File and the MPCF file and extracts the forces
        in a dictory with the rigid element as the key and the property2forces dict as the value
        """
        reader = FemFileReader(self.fem_file_path, block_size)
        reader.bulid_node2property()
        reader.get_rigid_elements()

        rigid_element2forces = {}

        for rigid_element in reader.rigid_elements:
            rigid_element.sort_nodes_by_property(reader.node2property)

            node2forces = MPCForcesReader(self.mpc_file_path).get_nodes2forces()

            property2forces = rigid_element.sum_forces_by_property(node2forces)
            rigid_element2forces[rigid_element] = property2forces

        return rigid_element2forces

    def write_suammry(self, rigid_element2property2forces: dict, file_path_out: str):
        """
        This method writes the summary of the forces extracted from the MPC forces file
        """
        if os.path.exists(file_path_out):
            os.remove(file_path_out)

        os.makedirs(os.path.dirname(file_path_out), exist_ok=True)

        timestamp = time.time()
        local_time = time.localtime(timestamp)
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)

        with open(file_path_out, "w", encoding="utf-8") as file:
            file.write("Summary of the MPC forces extraction\n")
            file.write(f"Date: {formatted_time}\n")
            file.write(f"Input FEM file: {self.fem_file_path}\n")
            file.write(f"Input MPC forces file: {self.mpc_file_path}\n")
            file.write("\n")

            for rigid_element, property2forces in rigid_element2property2forces.items():
                file.write(f"Rigid Element ID: {rigid_element.element_id}\n")
                master_node_id = list(rigid_element.master_node.keys())[0]
                file.write(f"  Master Node ID: {master_node_id}\n")
                master_node_coords = rigid_element.master_node[master_node_id]
                file.write(f"  Master Node Coords: {master_node_coords}\n")

                file.write(f"  Slave Nodes: {len(rigid_element.nodes)}\n")
                for property_id in sorted(property2forces.keys()):
                    forces = property2forces[property_id]
                    file.write(f"  Property ID: {property_id}\n")
                    file.write(
                        f"    Slave Nodes: {len(rigid_element.property2nodes[property_id])}\n"
                    )
                    force_names = ["FX", "FY", "FZ", "MX", "MY", "MZ"]
                    for force, force_name in zip(forces, force_names):
                        file.write(f"    {force_name}: {force:.3f}\n")
                file.write("\n")


def main():
    """ "
    This is the main function that is used to test the MPCForceExtractor class
    Its there because of a entry point in the toml file
    """

    input_folder = "data/input"
    output_folder = "data/output"

    # mpc_force_extractor = MPCForceExtractor(
    #     input_folder + "/PlateSimpleRBE3.fem",
    #     input_folder + "/PlateSimpleRBE3.mpcf",
    # )
    # mpc_force_extractor = MPCForceExtractor(
    #     input_folder + "/PlateSimpleRigid.fem",
    #     input_folder + "/PlateSimpleRigid.mpcf",
    # )
    mpc_force_extractor = MPCForceExtractor(
        input_folder + "/PlateSimpleRigid2.fem",
        input_folder + "/PlateSimpleRigid2.mpcf",
    )
    blocksize = 8

    rigidelement2forces = mpc_force_extractor.get_mpc_forces(blocksize)
    mpc_force_extractor.write_suammry(
        rigidelement2forces, output_folder + "/mpcforces_summary/output.txt"
    )


if __name__ == "__main__":
    main()
