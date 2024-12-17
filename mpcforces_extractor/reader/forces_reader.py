from typing import List
import time
from mpcforces_extractor.datastructure.subcases import Subcase, ForceType


class ForcesReader:
    """
    Class to read the MPC / SPC forces file and extract the forces for each node
    """

    file_path: str = None
    file_content: str = None

    def __init__(self, file_path):
        self.file_path = file_path
        print(f"Reading forces file: {file_path}")
        start_time = time.time()
        self.file_content = self.__read_lines()
        print("..took ", round(time.time() - start_time, 2), "seconds")
        self.node_ids = []

    def __read_lines(self) -> List[str]:
        """
        This method reads the lines of the MPC forces file
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            return file.readlines()
        return []

    def build_subcases(self, force_type: ForceType) -> None:
        """
        This method is used to extract the forces from the MPC forces file
        and build the subcases
        """
        subcase_id = 0
        subcase_time = 0
        subcase = None

        print(f"Building subcases data from {force_type.name}")
        start_time = time.time()
        for i, _ in enumerate(self.file_content):
            line = self.file_content[i].strip()

            if line.startswith("$SUBCASE"):
                subcase_id = int(line[0:23].replace("$SUBCASE", "").strip())
            if line.startswith("$TIME"):
                subcase_time = float(line.replace("$TIME", "").strip())
                if Subcase.get_subcase_by_id(subcase_id):
                    subcase = Subcase.get_subcase_by_id(subcase_id)
                else:
                    subcase = Subcase(subcase_id, subcase_time)

            if "X-FORCE" in line:
                i += 1
                line = self.file_content[i].strip()
                # first index of + in line
                first_column_length = line.find("+")

                i += 1
                line = self.file_content[i].strip()
                while i < len(self.file_content):

                    line = self.file_content[i]
                    if line.strip() == "":
                        i += 1
                        continue

                    # take the first_column_length characters as the node id
                    try:
                        node_id = int(line[:first_column_length].strip())
                    except ValueError:
                        i += 1
                        continue

                    # take the next 13 characters as the force values
                    n = 13
                    line_content = [
                        line[j : j + n]
                        for j in range(first_column_length, len(line), n)
                    ]
                    line_content = line_content[:-1]
                    for j, _ in enumerate(line_content):
                        line_content[j] = line_content[j].strip()

                    if len(line_content) < 6:
                        line_content += [""] * (6 - len(line_content))

                    force_x = float(line_content[0]) if line_content[0] != "" else 0
                    force_y = float(line_content[1]) if line_content[1] != "" else 0
                    force_z = float(line_content[2]) if line_content[2] != "" else 0
                    moment_x = float(line_content[3]) if line_content[3] != "" else 0
                    moment_y = float(line_content[4]) if line_content[4] != "" else 0
                    moment_z = float(line_content[5]) if line_content[5] != "" else 0

                    force = [force_x, force_y, force_z, moment_x, moment_y, moment_z]

                    subcase.add_force(node_id, force, force_type)
                    self.node_ids.append(node_id)

                    i += 1

        print("..took ", round(time.time() - start_time, 2), "seconds")
