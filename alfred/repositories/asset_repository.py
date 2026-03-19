from sqlalchemy import select

from alfred.models import Asset


class AssetRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def create(
        self,
        *,
        name: str,
        category: str | None,
        location: str | None,
        brand: str | None,
        model: str | None,
        serial_number: str | None,
        details: str | None,
    ) -> Asset:
        with self.session_factory.get_session() as session:
            asset = Asset(
                name=name,
                category=category,
                location=location,
                brand=brand,
                model=model,
                serial_number=serial_number,
                details=details,
            )
            session.add(asset)
            session.commit()
            session.refresh(asset)
            return asset

    def get_by_id(self, asset_id: int) -> Asset | None:
        statement = select(Asset).where(Asset.id == asset_id)

        with self.session_factory.get_session() as session:
            return session.scalar(statement)

    def list_recent(self, limit: int = 10) -> list[Asset]:
        statement = (
            select(Asset)
            .where(Asset.retired_at.is_(None))
            .order_by(Asset.created_at.desc(), Asset.id.desc())
            .limit(limit)
        )

        with self.session_factory.get_session() as session:
            return list(session.scalars(statement))