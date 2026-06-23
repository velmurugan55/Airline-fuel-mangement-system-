"""
Report Use Cases — invoice report and dashboard analytics.
"""

from decimal import Decimal
from collections import defaultdict
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from application.repositories.transaction_repository import TransactionRepository
from application.dto.report_dto import (
    ReportFilterDTO,
    InvoiceReportItemDTO,
    InvoiceReportResponseDTO,
    DashboardResponseDTO,
    TopAirlineDTO,
    TopVendorDTO,
)
import logging

logger = logging.getLogger(__name__)


class ReportUsecase:

    def __init__(self, db: Session):
        self.txn_repo = TransactionRepository(db)

    async def invoice_report(self, filters: ReportFilterDTO) -> InvoiceReportResponseDTO:
        """
        Returns a filtered list of invoice line items with aggregated totals.
        """
        txns = self.txn_repo.get_all(
            from_date=filters.from_date,
            to_date=filters.to_date,
            airline_id=filters.airline_id,
            vendor_id=filters.vendor_id,
        )

        items = []
        total_fuel = Decimal("0")
        total_amount = Decimal("0")

        for t in txns:
            items.append(
                InvoiceReportItemDTO(
                    invoice_no=t.invoice_no,
                    transaction_date=t.transaction_date,
                    airline_name=t.airline.airline_name,
                    airline_code=t.airline.airline_code,
                    vendor_name=t.vendor.vendor_name,
                    vendor_code=t.vendor.vendor_code,
                    fuel_quantity=t.fuel_quantity,
                    fuel_price=t.fuel_price,
                    total_amount=t.total_amount,
                    remarks=t.remarks,
                )
            )
            total_fuel += Decimal(str(t.fuel_quantity))
            total_amount += Decimal(str(t.total_amount))

        return InvoiceReportResponseDTO(
            total_records=len(items),
            total_fuel_quantity=total_fuel,
            total_amount=total_amount,
            invoices=items,
        )

    async def dashboard_report(self, filters: ReportFilterDTO) -> DashboardResponseDTO:
        """
        Returns KPI dashboard: total transactions, fuel, revenue,
        and top 5 airlines/vendors by fuel consumed.
        """
        txns = self.txn_repo.get_all(
            from_date=filters.from_date,
            to_date=filters.to_date,
            airline_id=filters.airline_id,
            vendor_id=filters.vendor_id,
        )

        total_fuel = Decimal("0")
        total_revenue = Decimal("0")
        airline_map: dict = defaultdict(lambda: {"name": "", "fuel": Decimal("0"), "amount": Decimal("0")})
        vendor_map: dict = defaultdict(lambda: {"name": "", "fuel": Decimal("0"), "amount": Decimal("0")})

        for t in txns:
            qty = Decimal(str(t.fuel_quantity))
            amt = Decimal(str(t.total_amount))
            total_fuel += qty
            total_revenue += amt

            airline_map[t.airline_id]["name"] = t.airline.airline_name
            airline_map[t.airline_id]["fuel"] += qty
            airline_map[t.airline_id]["amount"] += amt

            vendor_map[t.vendor_id]["name"] = t.vendor.vendor_name
            vendor_map[t.vendor_id]["fuel"] += qty
            vendor_map[t.vendor_id]["amount"] += amt

        top_airlines = sorted(
            [
                TopAirlineDTO(
                    airline_id=aid,
                    airline_name=v["name"],
                    total_fuel=v["fuel"],
                    total_amount=v["amount"],
                )
                for aid, v in airline_map.items()
            ],
            key=lambda x: x.total_fuel,
            reverse=True,
        )[:5]

        top_vendors = sorted(
            [
                TopVendorDTO(
                    vendor_id=vid,
                    vendor_name=v["name"],
                    total_fuel=v["fuel"],
                    total_amount=v["amount"],
                )
                for vid, v in vendor_map.items()
            ],
            key=lambda x: x.total_fuel,
            reverse=True,
        )[:5]

        return DashboardResponseDTO(
            period_from=filters.from_date,
            period_to=filters.to_date,
            total_transactions=len(txns),
            total_fuel_quantity=total_fuel,
            total_revenue=total_revenue,
            top_airlines=top_airlines,
            top_vendors=top_vendors,
        )
