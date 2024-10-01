import os
import time
from mpcforces_extractor.reader.modelreaders import FemFileReader
from mpcforces_extractor.datastructure.loads import Force, Moment
from mpcforces_extractor.force_extractor import MPCForceExtractor


class SummaryWriter:
    """
    This class is used to write the summary of the forces extracted from the MPC forces file
    """

    def __init__(self, instance: MPCForceExtractor, output_folder: str):
        self.instance = instance
        self.output_path = os.path.join(output_folder, "summary.txt")
        self.lines = []
        self.start_time = time.time()

    def add_header(self):
        """
        This method adds the header to the summary
        """
        timestamp = time.time()
        local_time = time.localtime(timestamp)
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)

        self.lines.append("Summary of the MPC forces extraction\n")
        self.lines.append(f"Date: {formatted_time}\n")
        self.lines.append(f"Input FEM file: {self.instance.fem_file_path}\n")
        self.lines.append(f"Input MPC forces file: {self.instance.mpc_file_path}\n")
        self.lines.append("\n")

    def add_mpc_lines(self, mpc_element2part2forces: dict):
        """
        This method adds the lines for each MPC element to the summary
        """
        for mpc, part_id2forces in mpc_element2part2forces.items():
            self.add_mpc_line(mpc, part_id2forces)

    def add_mpc_line(self, mpc, part_id2forces):
        """
        Add info for a single MPC element
        """
        self.lines.append(f"Rigid Element ID: {mpc.element_id}\n")
        self.lines.append(f"  MPC Config: {mpc.mpc_config.name}\n")

        # Forces present
        for _, load in FemFileReader.load_id2load.items():
            load_x = round(load.compenents[0], 3)
            load_y = round(load.compenents[1], 3)
            load_z = round(load.compenents[2], 3)
            # check if load is instance of force or a moment
            load_type = "None"
            if isinstance(load, Force):
                load_type = "Force"
            if isinstance(load, Moment):
                load_type = "Moment"

            if load.node_id in [mpc.master_node.id]:
                self.lines.append(
                    f"  {load_type} at Master ID: {load.id}; {load_x},{load_y},{load_z}\n"
                )
            if load.node_id in [node.id for node in mpc.nodes]:
                self.lines.append(
                    f"  {load_type} at Slave ID: {load.id}; {load_x},{load_y},{load_z}\n"
                )

        # 1D elements associated with the master node
        for element1D in self.instance.reader.elements_1D:
            if mpc.master_node in [element1D.node1, element1D.node2]:
                self.lines.append(
                    f"  1D Element ID: {element1D.id} associated with the master Node\n"
                )
        master_node = mpc.master_node

        if master_node.id in self.instance.node_id2forces:
            forces = self.instance.node_id2forces[master_node.id]
            self.lines.append(f"  Master Node ID: {master_node.id}, Forces: {forces}\n")
        else:
            self.lines.append(f"  Master Node ID: {master_node.id}\n")
        self.lines.append(f"  Master Node Coords: {master_node.coords}\n")
        self.lines.append(f"  Slave Nodes: {len(mpc.nodes)}\n")
        self.add_mpc_parts(mpc, part_id2forces)
        self.lines.append("\n")

    def add_mpc_parts(self, mpc, part_id2forces):
        """
        Add info for each part of the MPC element
        """
        for part_id in sorted(part_id2forces.keys()):
            number_of_slave_nodes = len(mpc.part_id2node_ids[part_id])
            if number_of_slave_nodes == 0:
                continue
            forces = part_id2forces[part_id]
            self.lines.append(f"  Part ID: {part_id}\n")
            node_ids = mpc.part_id2node_ids[part_id]
            self.lines.append(f"    First 5 Slave Nodes for Location {node_ids[1:6]}\n")
            self.lines.append(f"    Slave Nodes: {len(node_ids)}\n")
            force_names = ["FX", "FY", "FZ", "MX", "MY", "MZ"]
            for force, force_name in zip(forces, force_names):
                self.lines.append(f"    {force_name}: {force:.3f}\n")

    def write_lines(self):
        """
        This method writes the lines to the file
        """
        with open(self.output_path, "w", encoding="utf-8") as file:
            for line in self.lines:
                file.write(line)
        print("Summary written to", self.output_path)
        print("..took ", round(time.time() - self.start_time, 2), "seconds")