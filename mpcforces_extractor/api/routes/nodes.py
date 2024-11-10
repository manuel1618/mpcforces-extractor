from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from mpcforces_extractor.api.db.database import NodeDBModel
from mpcforces_extractor.api.dependencies import get_db
from mpcforces_extractor.api.config import ITEMS_PER_PAGE

router = APIRouter()


@router.get("", response_model=List[NodeDBModel])
async def get_nodes(
    page: int = Query(1, ge=1), db=Depends(get_db)
) -> List[NodeDBModel]:
    """
    Get nodes with pagination (fixed 100 items per page)
    """
    # Calculate offset based on the current page
    offset = (page - 1) * ITEMS_PER_PAGE

    # Fetch nodes from the database with the calculated offset and limit (fixed at 100)
    nodes = await db.get_nodes(offset=offset, limit=ITEMS_PER_PAGE)

    # Handle case when no nodes are found
    if not nodes:
        raise HTTPException(status_code=404, detail="No nodes found")

    return nodes


@router.get("/all", response_model=List[NodeDBModel])
async def get_all_nodes(db=Depends(get_db)) -> int:
    """
    Get all nodes
    """

    nodes = await db.get_all_nodes()

    if not nodes:
        raise HTTPException(status_code=404, detail="No nodes found")

    return nodes


class FilterDataModel(BaseModel):
    """
    Model for filter data.
    """

    ids: List[str]  # List of strings to handle IDs and ranges


@router.post("/filter", response_model=List[NodeDBModel])
async def get_nodes_filtered(
    filter_data: FilterDataModel, db=Depends(get_db)
) -> List[NodeDBModel]:
    """
    Get nodes filtered by a string, get it from all nodes, not paginated.
    The filter can be a range like '1-3' or comma-separated values like '1,2,3'.
    """
    nodes = await db.get_all_nodes()
    filtered_nodes = []

    if not filter_data:
        return filtered_nodes

    # Split the filter string by comma and process each part

    for part in filter_data.ids:
        part = part.strip()  # Trim whitespace (just to be sure)
        if "-" in part:
            # Handle range like '1-3'
            start, end = part.split("-")
            try:
                start_id = int(start.strip())
                end_id = int(end.strip())
                filtered_nodes.extend(
                    node for node in nodes if start_id <= node.id <= end_id
                )
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Invalid range in filter"
                ) from ValueError
        else:
            # Handle single ID
            try:
                node_id = int(part)
                node = next((node for node in nodes if node.id == node_id), None)
                if node:
                    filtered_nodes.append(node)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Invalid ID in filter"
                ) from ValueError
    return filtered_nodes
