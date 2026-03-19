from datetime import UTC, datetime

from alfred.models import Purchase
from alfred.repositories import PurchaseRepository


class PurchaseService:
    def __init__(self, repository: PurchaseRepository) -> None:
        self.repository = repository

    def record(
        self,
        item_name: str,
        vendor: str | None = None,
        purchase_date: datetime | None = None,
        price_amount: str | None = None,
        currency: str | None = None,
        order_reference: str | None = None,
        details: str | None = None,
    ) -> Purchase:
        item_name = item_name.strip()
        vendor = vendor.strip() if vendor is not None else None
        price_amount = price_amount.strip() if price_amount is not None else None
        currency = currency.strip() if currency is not None else None
        order_reference = order_reference.strip() if order_reference is not None else None
        details = details.strip() if details is not None else None

        if not item_name:
            raise ValueError("Item name cannot be empty.")

        if vendor == "":
            vendor = None

        if purchase_date is None:
            purchase_date = datetime.now(UTC)

        if price_amount == "":
            price_amount = None

        if currency == "":
            currency = None

        if order_reference == "":
            order_reference = None

        if details == "":
            details = None

        return self.repository.create(
            item_name=item_name,
            vendor=vendor,
            purchase_date=purchase_date,
            price_amount=price_amount,
            currency=currency,
            order_reference=order_reference,
            details=details,
        )

    def list_recent(self, limit: int = 20) -> list[Purchase]:
        return self.repository.list_recent(limit=limit)