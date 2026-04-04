from datetime import UTC, datetime

from sqlalchemy import select

from alfred.models import MaintenanceRecord


class MaintenanceRecordRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def create(
        self,
        subject: str,
        category: str | None,
        performed_at: datetime,
        details: str,
        notes: str | None,
    ) -> MaintenanceRecord:
        with self.session_factory.get_session() as session:
            maintenance_record = MaintenanceRecord(
                subject=subject,
                category=category,
                performed_at=performed_at,
                details=details,
                notes=notes,
            )
            session.add(maintenance_record)
            session.commit()
            session.refresh(maintenance_record)
            return maintenance_record

    def get_by_id(self, maintenance_record_id: int) -> MaintenanceRecord | None:
        statement = select(MaintenanceRecord).where(
            MaintenanceRecord.id == maintenance_record_id
        )

        with self.session_factory.get_session() as session:
            return session.scalar(statement)

    def update(
        self,
        maintenance_record: MaintenanceRecord,
        *,
        category: str | None,
        performed_at: datetime,
        details: str,
        notes: str | None,
    ) -> MaintenanceRecord:
        with self.session_factory.get_session() as session:
            persisted_maintenance_record = session.get(
                MaintenanceRecord,
                maintenance_record.id,
            )

            if persisted_maintenance_record is None:
                return maintenance_record

            persisted_maintenance_record.category = category
            persisted_maintenance_record.performed_at = performed_at
            persisted_maintenance_record.details = details
            persisted_maintenance_record.notes = notes
            persisted_maintenance_record.updated_at = datetime.now(UTC)

            session.add(persisted_maintenance_record)
            session.commit()
            session.refresh(persisted_maintenance_record)
            return persisted_maintenance_record

    def retire(
        self,
        maintenance_record: MaintenanceRecord,
        *,
        reason: str | None,
    ) -> MaintenanceRecord:
        with self.session_factory.get_session() as session:
            persisted_maintenance_record = session.get(
                MaintenanceRecord,
                maintenance_record.id,
            )

            if persisted_maintenance_record is None:
                return maintenance_record

            persisted_maintenance_record.retired_at = datetime.now(UTC)
            persisted_maintenance_record.retired_reason = reason

            session.add(persisted_maintenance_record)
            session.commit()
            session.refresh(persisted_maintenance_record)
            return persisted_maintenance_record

    def list_recent(self, limit: int = 10) -> list[MaintenanceRecord]:
        statement = (
            select(MaintenanceRecord)
            .where(MaintenanceRecord.retired_at.is_(None))
            .order_by(
                MaintenanceRecord.performed_at.desc(),
                MaintenanceRecord.created_at.desc(),
                MaintenanceRecord.id.desc(),
            )
            .limit(limit)
        )

        with self.session_factory.get_session() as session:
            return list(session.scalars(statement))