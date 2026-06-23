"""
Transaction Use Cases — business logic for fuel transaction management.

Business Rules Enforced:
  - Rule #2: Latest fuel price auto-selected from vendor's price table.
  - Rule #3: Invoice number format INV-YYYYMMDD-XXXX.
  - Rule #4: total_amount = fuel_quantity × fuel_price.
  - Rule #5: If fuel price doesn't exist, prevent transaction creation.
"""

from datetime import date
from sqlalchemy.orm import Session

from application.repositories.transaction_repository import TransactionRepository
from application.repositories.fuel_price_repository import FuelPriceRepository
from application.repositories.airline_repository import AirlineRepository
from application.repositories.vendor_repository import VendorRepository
from application.providers.invoice_provider import generate_invoice_no, build_invoice_data
from application.dto.transaction_dto import (
    TransactionCreateDTO,
    TransactionResponseDTO,
    InvoiceResponseDTO,
    TransactionListResponseDTO,
)
from application.exception.not_found_exception import NotFoundException
from application.exception.custom_exception import FuelPriceNotFoundException
import logging

logger = logging.getLogger(__name__)


class TransactionUsecase:

    def __init__(self, db: Session):
        self.repo = TransactionRepository(db)
        self.price_repo = FuelPriceRepository(db)
        self.airline_repo = AirlineRepository(db)
        self.vendor_repo = VendorRepository(db)
        self.db = db

    async def create_transaction(self, dto: TransactionCreateDTO) -> TransactionResponseDTO:
        # Validate airline exists
        airline = self.airline_repo.get_by_id(dto.airline_id)
        if not airline:
            raise NotFoundException("Airline", dto.airline_id)

        # Validate vendor exists
        vendor = self.vendor_repo.get_by_id(dto.vendor_id)
        if not vendor:
            raise NotFoundException("Vendor", dto.vendor_id)

        # Rule #5: Fuel price must exist — raise error if not found
        latest_price = self.price_repo.get_latest_by_vendor(dto.vendor_id)
        if not latest_price:
            raise FuelPriceNotFoundException(dto.vendor_id)

        # Rule #4: Calculate total
        fuel_price = latest_price.price_per_liter
        total_amount = dto.fuel_quantity * fuel_price

        # Rule #3: Generate unique invoice number
        invoice_no = await self.generate_invoice_no(dto.transaction_date)

        txn = self.repo.create(
            invoice_no=invoice_no,
            airline_id=dto.airline_id,
            vendor_id=dto.vendor_id,
            fuel_quantity=dto.fuel_quantity,
            fuel_price=fuel_price,
            total_amount=total_amount,
            transaction_date=dto.transaction_date,
            remarks=dto.remarks,
        )
        return TransactionResponseDTO.model_validate(txn)

    async def generate_invoice_no(self, transaction_date: date) -> str:
        """Delegate invoice number generation to the invoice provider."""
        return generate_invoice_no(self.db, transaction_date)

    async def get_invoice(self, invoice_no: str) -> InvoiceResponseDTO:
        txn = self.repo.get_by_invoice_no(invoice_no)
        if not txn:
            raise NotFoundException("Transaction", invoice_no)
        data = build_invoice_data(txn)
        return InvoiceResponseDTO(**data)

    async def get_transactions(
        self,
        from_date=None,
        to_date=None,
        airline_id=None,
        vendor_id=None,
    ) -> TransactionListResponseDTO:
        txns = self.repo.get_all(
            from_date=from_date,
            to_date=to_date,
            airline_id=airline_id,
            vendor_id=vendor_id,
        )
        return TransactionListResponseDTO(
            total=len(txns),
            data=[TransactionResponseDTO.model_validate(t) for t in txns],
        )
