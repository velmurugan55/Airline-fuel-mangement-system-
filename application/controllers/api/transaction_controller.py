"""
Transaction Controller — fuel transaction endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from application.providers.database import get_db
from application.controllers.api.dependencies import get_current_user
from application.usecases.transaction_usecase import TransactionUsecase
from application.dto.transaction_dto import (
    TransactionCreateDTO,
    TransactionResponseDTO,
    InvoiceResponseDTO,
)

router = APIRouter(prefix="/transactions", tags=["Fuel Transactions"])


@router.post(
    "",
    response_model=TransactionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new fuel transaction",
)
async def create_transaction(
    dto: TransactionCreateDTO,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
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
    return await TransactionUsecase(db).create_transaction(dto)


@router.get(
    "/{invoice_no}",
    response_model=InvoiceResponseDTO,
    summary="Get transaction invoice by invoice number",
)
async def get_invoice(
    invoice_no: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Retrieve full invoice details by invoice number (e.g. `INV-20240622-0001`).
    Returns nested airline and vendor information.
    """
    return await TransactionUsecase(db).get_invoice(invoice_no)
