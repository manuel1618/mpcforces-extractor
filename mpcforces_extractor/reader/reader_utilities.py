import os
from typing import List


class modelReaderUtilities:
    """
    This class contains methods for the model reader which
    are just utility methods and could be used by other readers as well
    """

    @staticmethod
    def node_coord_parser(coord_str: str) -> float:
        """
        This method is used to parse the node coordinates
        """
        # Problem is the expenential notation without the E in it
        before_dot = coord_str.split(".")[0]
        after_dot = coord_str.split(".")[1]
        if "-" in after_dot:
            return float(before_dot + "." + after_dot.replace("-", "e-"))
        if "+" in after_dot:
            return float(before_dot + "." + after_dot.replace("+", "e+"))

        return float(coord_str)

    @staticmethod
    def split_line(line: str, blocksize: int) -> List:
        """
        This method is used to split a line into blocks of blocksize, and
        remove the newline character and strip the content of the block
        """
        line_content = [line[j : j + blocksize] for j in range(0, len(line), blocksize)]

        if "\n" in line_content:
            line_content.remove("\n")

        line_content = [line.strip() for line in line_content]
        return line_content

    @staticmethod
    def get_chunks(lines: List[str], number_of_splits=0):
        """
        This method is used to split the node lines into chunks for parallel processing
        """

        if number_of_splits == 0:
            number_of_processes = os.cpu_count()
            number_of_splits = min(len(lines), number_of_processes)

        chunk_size = len(lines) // number_of_splits
        chunk_indices = [i * chunk_size for i in range(number_of_splits)]
        # shift the indices to the right as long as the index points to a line that starts with a + (continuation line)
        for i, _ in enumerate(chunk_indices):
            while lines[chunk_indices[i]].startswith("+"):
                chunk_indices[i] += 1
        chunks = [
            lines[chunk_indices[i] : chunk_indices[i + 1]]
            for i in range(number_of_splits - 1)
        ]
        chunks.append(lines[chunk_indices[-1] :])

        return chunks
