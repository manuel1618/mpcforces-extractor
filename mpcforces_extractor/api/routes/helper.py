from typing import List
from pydantic import BaseModel


class FilterDataModel(BaseModel):
    """
    Model for filter data.
    """

    ids: List[str]  # List of strings to handle IDs and ranges


def expand_filter_string(filter_data: FilterDataModel) -> List[int]:
    """
    HELPER METHOD
    Get nodes filtered by a string, get it from all nodes, not paginated.
    The filter can be a range like '1-3' or comma-separated values like '1,2,3'.
    """
    filtered_nodes = []

    if not filter_data:
        return filtered_nodes

    # Split the filter string by comma and process each part

    for filter_part in filter_data.ids:
        # Check if the filter part contains a range
        if "-" in filter_part:
            # Split the range by '-' and convert the parts into integers
            start, end = map(int, filter_part.split("-"))

            # Add the range of nodes to the filtered nodes list
            filtered_nodes.extend(range(start, end + 1))
        else:
            # Convert the filter part into an integer and add it to the filtered nodes list
            filtered_nodes.append(int(filter_part))

    return filtered_nodes
