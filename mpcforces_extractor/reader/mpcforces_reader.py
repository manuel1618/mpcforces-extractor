from typing import List
from mpcforces_extractor.datastructure.subcases import Subcase


class MPCForcesReader:
    """
    Class to read the MPC forces file and extract the forces for each node
    """

    file_path: str = None
    file_content: str = None

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_content = self.__read_lines()

    def __read_lines(self) -> List[str]:
        """
        This method reads the lines of the MPC forces file
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            return file.readlines()
        return []

    def bulid_subcases(self) -> None:
        """
        This method is used to extract the forces from the MPC forces file
        and build the subcases
        """
        subcase_id = 0
        time = 0
        Subcase.reset()
        subcase = None
        for i, _ in enumerate(self.file_content):
            line = self.file_content[i].strip()

            if line.startswith("$SUBCASE"):
                subcase_id = int(line.replace("$SUBCASE", "").strip())
            if line.startswith("$TIME"):
                time = float(line.replace("$TIME", "").strip())
                subcase = Subcase(subcase_id, time)

            if "X-FORCE" in line:
                i += 2
                line = self.file_content[i].strip()
                while (
                    not self.file_content[i].startswith("---")
                    and not self.file_content[i].strip() == ""
                ):
                    line = self.file_content[i]

                    # take the first 8 characters as the node id
                    node_id = int(line[:8].strip())

                    # take the next 13 characters as the force values
                    n = 13
                    line_content = [line[j : j + n] for j in range(8, len(line), n)]
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

                    subcase.add_force(node_id, force)

                    i += 1
