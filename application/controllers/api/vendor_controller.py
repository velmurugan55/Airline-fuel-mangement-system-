"""
Vendor Controller — CRUD endpoints for fuel vendors.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.usecases.vendor_usecase import VendorUsecase
from application.dto.vendor_dto import (
    VendorCreateDTO,
    VendorUpdateDTO,
    VendorResponseDTO,
    VendorListResponseDTO,
)

router = APIRouter(prefix="/vendors", tags=["Fuel Vendors"])


@router.post(
    "",
    response_model=VendorResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new fuel vendor",
)
async def create_vendor(
    dto: VendorCreateDTO,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    **Sample Request:**
    ```json
    {
      "vendor_code": "PT-FUEL",
      "vendor_name": "PT Pertamina Fuel",
      "contact_person": "Jane Smith",
      "email": "contact@pertamina.com",
      "phone": "+62-21-1234-5678",
      "address": "Jakarta Pusat, DKI Jakarta"
    }
    ```
    """
    return await VendorUsecase(db).create_vendor(dto)


@router.get(
    "",
    response_model=VendorListResponseDTO,
    summary="List all fuel vendors",
)
async def get_all_vendors(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return await VendorUsecase(db).get_all_vendors()


@router.get(
    "/{vendor_id}",
    response_model=VendorResponseDTO,
    summary="Get fuel vendor by ID",
)
async def get_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return await VendorUsecase(db).get_vendor(vendor_id)


@router.put(
    "/{vendor_id}",
    response_model=VendorResponseDTO,
    summary="Update a fuel vendor",
)
async def update_vendor(
    vendor_id: int,
    dto: VendorUpdateDTO,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return await VendorUsecase(db).update_vendor(vendor_id, dto)


@router.delete(
    "/{vendor_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a fuel vendor",
)
async def delete_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return await VendorUsecase(db).delete_vendor(vendor_id)
