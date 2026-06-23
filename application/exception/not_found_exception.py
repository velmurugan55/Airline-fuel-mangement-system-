"""
Not Found Exception.
"""

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    def __init__(self, resource: str = "Resource", identifier: str | int = ""):
        detail = f"{resource} not found."
        if identifier:
            detail = f"{resource} with id '{identifier}' not found."
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
