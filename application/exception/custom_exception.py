"""
Custom application exceptions.
"""

from fastapi import HTTPException, status


class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class FuelPriceNotFoundException(HTTPException):
    """
    Raised when no fuel price exists for a vendor at transaction creation time.
    Returns 422 Unprocessable Content (Business Rule #5).
    """
    def __init__(self, vendor_id: int):
        super().__init__(
            # Use the integer directly — avoids the renamed-constant deprecation warning
            # across FastAPI / Starlette versions (HTTP_422_UNPROCESSABLE_ENTITY vs _CONTENT)
            status_code=422,
            detail=(
                f"No active fuel price found for vendor_id={vendor_id}. "
                "Please set a fuel price before creating a transaction."
            ),
        )
