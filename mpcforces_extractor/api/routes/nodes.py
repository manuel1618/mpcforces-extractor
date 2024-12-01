from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from mpcforces_extractor.api.db.database import NodeDBModel
from mpcforces_extractor.api.dependencies import get_db
from mpcforces_extractor.api.config import ITEMS_PER_PAGE
from mpcforces_extractor.api.db.database import Database
from mpcforces_extractor.api.routes.helper import FilterDataModel, expand_filter_string

router = APIRouter()


# Route to get nodes with pagination, sorting, and filtering
@router.post("", response_model=List[NodeDBModel])
async def get_nodes(
    page: int = Query(1, ge=1),  # Pagination
    *,
    sort_column: str = Query("id", alias="sortColumn"),  # Sorting column
    sort_direction: int = Query(
        1, ge=-1, le=1, alias="sortDirection"
    ),  # Sorting direction: 1 (asc) or -1 (desc)
    filter_data: FilterDataModel,
    db: Database = Depends(get_db),  # Dependency for DB session
    subcase_id: int = Query(None, alias="subcaseId"),
) -> List[NodeDBModel]:
    """
    Get nodes with pagination, sorting, and optional filtering by IDs.
    """
    # Calculate offset based on the current page
    offset = (page - 1) * ITEMS_PER_PAGE

    # Handle filtering if filter_ids is provided
    node_ids = expand_filter_string(filter_data)

    # Fetch nodes from the database with the calculated offset, limit, sorting, and filtering
    nodes = await db.get_nodes(
        offset=offset,
        limit=ITEMS_PER_PAGE,
        sort_column=sort_column,
        sort_direction=sort_direction,
        node_ids=node_ids,
        subcase_id=subcase_id,
    )

    # Handle case when no nodes are found
    if not nodes:
        raise HTTPException(status_code=404, detail="No nodes found")

    return nodes


@router.post("/all", response_model=List[NodeDBModel])
async def get_all_nodes(filter_data: FilterDataModel, db=Depends(get_db)) -> int:
    """
    Get all nodes
    """

    node_ids = expand_filter_string(filter_data)
    nodes = await db.get_all_nodes(node_ids)

    if not nodes:
        raise HTTPException(status_code=404, detail="No nodes found")

    return nodes
