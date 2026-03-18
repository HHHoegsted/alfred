from alfred.models import Asset
from alfred.repositories import AssetRepository


class AssetService:
    def __init__(self, repository: AssetRepository) -> None:
        self.repository = repository

    def record(
        self,
        name: str,
        category: str | None = None,
        location: str | None = None,
        brand: str | None = None,
        model: str | None = None,
        serial_number: str | None = None,
        details: str | None = None,
    ) -> Asset:
        name = name.strip()
        category = category.strip() if category is not None else None
        location = location.strip() if location is not None else None
        brand = brand.strip() if brand is not None else None
        model = model.strip() if model is not None else None
        serial_number = serial_number.strip() if serial_number is not None else None
        details = details.strip() if details is not None else None

        if not name:
            raise ValueError("Name cannot be empty.")

        if category == "":
            category = None

        if location == "":
            location = None

        if brand == "":
            brand = None

        if model == "":
            model = None

        if serial_number == "":
            serial_number = None

        if details == "":
            details = None

        return self.repository.create(
            name=name,
            category=category,
            location=location,
            brand=brand,
            model=model,
            serial_number=serial_number,
            details=details,
        )

    def list_recent(self, limit: int = 20) -> list[Asset]:
        return self.repository.list_recent(limit=limit)