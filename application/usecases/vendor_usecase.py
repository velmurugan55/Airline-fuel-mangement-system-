"""
Vendor Use Cases — business logic for fuel vendor management.
"""

from sqlalchemy.orm import Session

from application.repositories.vendor_repository import VendorRepository
from application.dto.vendor_dto import VendorCreateDTO, VendorUpdateDTO, VendorResponseDTO, VendorListResponseDTO
from application.exception.not_found_exception import NotFoundException
from application.exception.custom_exception import ConflictException
import logging

logger = logging.getLogger(__name__)


class VendorUsecase:

    def __init__(self, db: Session):
        self.repo = VendorRepository(db)

    async def create_vendor(self, dto: VendorCreateDTO) -> VendorResponseDTO:
        existing = self.repo.get_by_code(dto.vendor_code)
        if existing:
            raise ConflictException(f"Vendor with code '{dto.vendor_code}' already exists.")
        vendor = self.repo.create(dto)
        return VendorResponseDTO.model_validate(vendor)

    async def update_vendor(self, vendor_id: int, dto: VendorUpdateDTO) -> VendorResponseDTO:
        vendor = self.repo.get_by_id(vendor_id)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)
        updated = self.repo.update(vendor, dto)
        return VendorResponseDTO.model_validate(updated)

    async def delete_vendor(self, vendor_id: int) -> dict:
        vendor = self.repo.get_by_id(vendor_id)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)
        self.repo.delete(vendor)
        return {"message": f"Vendor id={vendor_id} deleted successfully."}

    async def get_vendor(self, vendor_id: int) -> VendorResponseDTO:
        vendor = self.repo.get_by_id(vendor_id)
        if not vendor:
            raise NotFoundException("Vendor", vendor_id)
        return VendorResponseDTO.model_validate(vendor)

    async def get_all_vendors(self) -> VendorListResponseDTO:
        vendors = self.repo.get_all()
        return VendorListResponseDTO(
            total=len(vendors),
            data=[VendorResponseDTO.model_validate(v) for v in vendors],
        )
