"""
Report Controller — invoice report and dashboard endpoints (with Redis cache).
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
from application.core.redis import get_redis
from application.services.cache_service import CacheService

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
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    """
    Returns a detailed invoice report with line items, totals, and aggregated
    fuel quantity and revenue. All filters are optional and combinable.
    Results are cached in Redis for 2 minutes.
    """
    cache_filters = {
        "from_date": str(from_date) if from_date else None,
        "to_date": str(to_date) if to_date else None,
        "airline_id": airline_id,
        "vendor_id": vendor_id,
    }
    cache = CacheService(redis)
    cached = await cache.get_invoice_report(cache_filters)
    if cached is not None:
        return cached

    dto = ReportFilterDTO(from_date=from_date, to_date=to_date, airline_id=airline_id, vendor_id=vendor_id)
    result = await ReportUsecase(db).invoice_report(dto)
    await cache.set_invoice_report(result, cache_filters)
    return result


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
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    """
    Returns dashboard KPIs (cached in Redis for 2 minutes):
    - Total transactions, fuel quantity, and revenue for the period
    - Top 5 airlines by fuel consumption
    - Top 5 vendors by fuel dispensed
    """
    cache_filters = {
        "from_date": str(from_date) if from_date else None,
        "to_date": str(to_date) if to_date else None,
        "airline_id": airline_id,
        "vendor_id": vendor_id,
    }
    cache = CacheService(redis)
    cached = await cache.get_dashboard(cache_filters)
    if cached is not None:
        return cached

    dto = ReportFilterDTO(from_date=from_date, to_date=to_date, airline_id=airline_id, vendor_id=vendor_id)
    result = await ReportUsecase(db).dashboard_report(dto)
    await cache.set_dashboard(result, cache_filters)
    return result
