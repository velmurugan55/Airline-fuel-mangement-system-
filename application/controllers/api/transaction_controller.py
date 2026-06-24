"""
Transaction Controller — fuel transaction endpoints (with cache invalidation + notifications).
"""

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.usecases.transaction_usecase import TransactionUsecase
from application.dto.transaction_dto import (
    TransactionCreateDTO,
    TransactionResponseDTO,
    InvoiceResponseDTO,
    TransactionListResponseDTO,
)
from application.core.redis import get_redis
from application.core.cache import INVALIDATE_ON_TRANSACTION_CHANGE
from application.services.cache_service import CacheService
from application.services.notification_service import NotificationService
from application.src.models.user_model import User

router = APIRouter(prefix="/transactions", tags=["Fuel Transactions"])


@router.post(
    "",
    response_model=TransactionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new fuel transaction",
)
async def create_transaction(
    dto: TransactionCreateDTO,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    """
    Record a fuel transaction. The system will:
    - Auto-select the latest fuel price for the selected vendor
    - Calculate `total_amount = fuel_quantity × fuel_price`
    - Generate a unique invoice number in format `INV-YYYYMMDD-XXXX`

    ⚠️ Returns **422** if no fuel price exists for the vendor.

    **Sample Request:**
    ```json
    {
      "airline_id": 1,
      "vendor_id": 1,
      "fuel_quantity": 5000.0000,
      "transaction_date": "2024-06-22",
      "remarks": "Regular refuelling – Flight GA-415"
    }
    ```

    **Sample Response:**
    ```json
    {
      "id": 1,
      "invoice_no": "INV-20240622-0001",
      "airline_id": 1,
      "vendor_id": 1,
      "fuel_quantity": 5000.0000,
      "fuel_price": 12500.0000,
      "total_amount": 62500000.0000,
      "transaction_date": "2024-06-22",
      "remarks": "Regular refuelling – Flight GA-415"
    }
    ```
    """
    result = await TransactionUsecase(db).create_transaction(dto)

    async def _post_create():
        cache = CacheService(redis)
        await cache.delete_many_patterns(INVALIDATE_ON_TRANSACTION_CHANGE)
        notif = NotificationService(redis)
        await notif.notify_new_transaction(
            current_user.id,
            result.invoice_no,
            float(result.total_amount),
        )

    background_tasks.add_task(_post_create)
    return result


@router.get(
    "",
    response_model=TransactionListResponseDTO,
    summary="List all fuel transactions",
)
async def get_all_transactions(
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    """Returns all fuel transactions, newest first (cached 60 s)."""
    from application.core.cache import CacheTTL, CacheKey
    cache = CacheService(redis)
    cached = await cache.get_transactions()
    if cached is not None:
        return cached
    result = await TransactionUsecase(db).get_transactions()
    await cache.set_transactions(result)
    return result


@router.get(
    "/{invoice_no}",
    response_model=InvoiceResponseDTO,
    summary="Get transaction invoice by invoice number",
)
async def get_invoice(
    invoice_no: str,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
    _=Depends(get_current_user),
):
    """
    Retrieve full invoice details by invoice number (e.g. `INV-20240622-0001`).
    Returns nested airline and vendor information.
    """
    from application.core.cache import CacheKey, CacheTTL
    cache = CacheService(redis)
    cached = await cache.get(CacheKey.transaction(invoice_no))
    if cached is not None:
        return cached
    result = await TransactionUsecase(db).get_invoice(invoice_no)
    await cache.set(CacheKey.transaction(invoice_no), result, CacheTTL.TRANSACTION_LIST)
    return result
