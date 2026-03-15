from alfred.models import Person
from alfred.repositories import PersonRepository


class PersonService:
    def __init__(self, repository: PersonRepository) -> None:
        self.repository = repository

    def register(
        self,
        name: str,
        is_household_member: bool = False,
    ) -> Person:
        return self.repository.create(
            name=name,
            is_household_member=is_household_member,
        )

    def list_recent(self, limit: int = 20) -> list[Person]:
        return self.repository.list_recent(limit=limit)