"""
Report Controller — invoice report and dashboard endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.usecases.report_usecase import ReportUsecase
from application.dto.report_dto import (
    ReportFilterDTO,
    InvoiceReportResponseDTO,
    DashboardResponseDTO,
)

router = APIRouter(prefix="/reports", tags=["Reports & Dashboard"])


@router.get(
    "/invoices",
    response_model=InvoiceReportResponseDTO,
    summary="Invoice report with filters",
)
async def invoice_report(
    from_date: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    airline_id: Optional[int] = Query(None, description="Filter by airline ID"),
    vendor_id: Optional[int] = Query(None, description="Filter by vendor ID"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Returns a detailed invoice report with line items, totals, and aggregated
    fuel quantity and revenue. All filters are optional and combinable.

    **Sample Request:**
    ```
    GET /reports/invoices?from_date=2024-01-01&to_date=2024-12-31&airline_id=1
    ```

    **Sample Response:**
    ```json
    {
      "total_records": 2,
      "total_fuel_quantity": 10000.0000,
      "total_amount": 125000000.0000,
      "invoices": [
        {
          "invoice_no": "INV-20240622-0001",
          "transaction_date": "2024-06-22",
          "airline_name": "Garuda Indonesia",
          "airline_code": "GA",
          "vendor_name": "PT Pertamina Fuel",
          "vendor_code": "PT-FUEL",
          "fuel_quantity": 5000.0000,
          "fuel_price": 12500.0000,
          "total_amount": 62500000.0000,
          "remarks": "Regular refuelling"
        }
      ]
    }
    ```
    """
    filters = ReportFilterDTO(
        from_date=from_date,
        to_date=to_date,
        airline_id=airline_id,
        vendor_id=vendor_id,
    )
    return await ReportUsecase(db).invoice_report(filters)


@router.get(
    "/dashboard",
    response_model=DashboardResponseDTO,
    summary="Dashboard KPI report",
)
async def dashboard_report(
    from_date: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    airline_id: Optional[int] = Query(None, description="Filter by airline ID"),
    vendor_id: Optional[int] = Query(None, description="Filter by vendor ID"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Returns dashboard KPIs:
    - Total transactions, fuel quantity, and revenue for the period
    - Top 5 airlines by fuel consumption
    - Top 5 vendors by fuel dispensed

    **Sample Response:**
    ```json
    {
      "period_from": "2024-01-01",
      "period_to": "2024-12-31",
      "total_transactions": 50,
      "total_fuel_quantity": 250000.0000,
      "total_revenue": 3125000000.0000,
      "top_airlines": [
        {
          "airline_id": 1,
          "airline_name": "Garuda Indonesia",
          "total_fuel": 100000.0000,
          "total_amount": 1250000000.0000
        }
      ],
      "top_vendors": [
        {
          "vendor_id": 1,
          "vendor_name": "PT Pertamina Fuel",
          "total_fuel": 200000.0000,
          "total_amount": 2500000000.0000
        }
      ]
    }
    ```
    """
    filters = ReportFilterDTO(
        from_date=from_date,
        to_date=to_date,
        airline_id=airline_id,
        vendor_id=vendor_id,
    )
    return await ReportUsecase(db).dashboard_report(filters)
