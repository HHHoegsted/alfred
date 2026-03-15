from sqlalchemy import select
from sqlalchemy.orm import Session

from alfred.models import Person


class PersonRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        name: str,
        is_household_member: bool = False,
    ) -> Person:
        person = Person(
            name=name,
            is_household_member=is_household_member,
        )
        self.session.add(person)
        self.session.commit()
        self.session.refresh(person)
        return person

    def list_recent(self, limit: int = 20) -> list[Person]:
        statement = (
            select(Person)
            .order_by(Person.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())
