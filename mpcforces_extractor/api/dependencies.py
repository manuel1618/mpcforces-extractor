from fastapi import Request, HTTPException


def get_db(request: Request):
    """
    Get the database session
    """
    if not hasattr(request.app, "db"):
        raise HTTPException(status_code=500, detail="Database not initialized")
    return request.app.db
