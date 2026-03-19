from datetime import datetime

from sqlalchemy import select

from alfred.models import Purchase


class PurchaseRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def create(
        self,
        *,
        item_name: str,
        vendor: str | None,
        purchase_date: datetime | None,
        price_amount: str | None,
        currency: str | None,
        order_reference: str | None,
        details: str | None,
    ) -> Purchase:
        with self.session_factory.get_session() as session:
            purchase = Purchase(
                item_name=item_name,
                vendor=vendor,
                purchase_date=purchase_date,
                price_amount=price_amount,
                currency=currency,
                order_reference=order_reference,
                details=details,
            )
            session.add(purchase)
            session.commit()
            session.refresh(purchase)
            return purchase

    def get_by_id(self, purchase_id: int) -> Purchase | None:
        statement = select(Purchase).where(Purchase.id == purchase_id)

        with self.session_factory.get_session() as session:
            return session.scalar(statement)

    def list_recent(self, limit: int = 10) -> list[Purchase]:
        statement = (
            select(Purchase)
            .where(Purchase.retired_at.is_(None))
            .order_by(Purchase.created_at.desc(), Purchase.id.desc())
            .limit(limit)
        )

        with self.session_factory.get_session() as session:
            return list(session.scalars(statement))