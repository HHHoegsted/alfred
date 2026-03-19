from sqlalchemy import select

from alfred.models import Person


class PersonRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def create(
        self,
        name: str,
        is_household_member: bool = False,
    ) -> Person:
        with self.session_factory.get_session() as session:
            person = Person(
                name=name,
                is_household_member=is_household_member,
            )
            session.add(person)
            session.commit()
            session.refresh(person)
            return person

    def list_recent(self, limit: int = 20) -> list[Person]:
        statement = (
            select(Person)
            .order_by(Person.created_at.desc())
            .limit(limit)
        )

        with self.session_factory.get_session() as session:
            return list(session.scalars(statement).all())