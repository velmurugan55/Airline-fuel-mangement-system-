"""
Fuel Transaction Repository — DB operations for FuelTransaction.
"""

from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload

from application.src.models.transaction_model import FuelTransaction
import logging

logger = logging.getLogger(__name__)


class TransactionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_invoice_no(self, invoice_no: str) -> Optional[FuelTransaction]:
        """Fetch a single transaction with airline and vendor eagerly loaded."""
        return (
            self.db.query(FuelTransaction)
            .options(
                joinedload(FuelTransaction.airline),
                joinedload(FuelTransaction.vendor),
            )
            .filter(FuelTransaction.invoice_no == invoice_no)
            .first()
        )

    def get_all(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        airline_id: Optional[int] = None,
        vendor_id: Optional[int] = None,
    ) -> List[FuelTransaction]:
        """
        Retrieve transactions with optional filters.
        Eagerly loads airline and vendor for report generation.
        """
        q = self.db.query(FuelTransaction).options(
            joinedload(FuelTransaction.airline),
            joinedload(FuelTransaction.vendor),
        )
        if from_date:
            q = q.filter(FuelTransaction.transaction_date >= from_date)
        if to_date:
            q = q.filter(FuelTransaction.transaction_date <= to_date)
        if airline_id:
            q = q.filter(FuelTransaction.airline_id == airline_id)
        if vendor_id:
            q = q.filter(FuelTransaction.vendor_id == vendor_id)
        return q.order_by(FuelTransaction.transaction_date.desc()).all()

    def create(
        self,
        invoice_no: str,
        airline_id: int,
        vendor_id: int,
        fuel_quantity: float,
        fuel_price: float,
        total_amount: float,
        transaction_date: date,
        remarks: Optional[str],
    ) -> FuelTransaction:
        txn = FuelTransaction(
            invoice_no=invoice_no,
            airline_id=airline_id,
            vendor_id=vendor_id,
            fuel_quantity=fuel_quantity,
            fuel_price=fuel_price,
            total_amount=total_amount,
            transaction_date=transaction_date,
            remarks=remarks,
        )
        self.db.add(txn)
        self.db.commit()
        self.db.refresh(txn)
        logger.info("Created transaction: %s  amount=%s", invoice_no, total_amount)
        return txn
