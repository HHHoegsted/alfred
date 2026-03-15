from pathlib import Path

from alfred.bootstrap import init_sqlalchemy
from alfred.models import HouseholdFact


def test_household_fact_can_be_inserted_and_queried(tmp_path: Path) -> None:
    session_factory = init_sqlalchemy(data_dir=tmp_path)

    with session_factory.get_session() as session:
        fact = HouseholdFact(
            subject="Water shutoff valve",
            value="Under kitchen sink",
            details="Turn clockwise to close",
        )
        session.add(fact)
        session.commit()

    with session_factory.get_session() as session:
        facts = session.query(HouseholdFact).all()

    assert len(facts) == 1
    assert facts[0].subject == "Water shutoff valve"
    assert facts[0].value == "Under kitchen sink"
    assert facts[0].details == "Turn clockwise to close"
    assert facts[0].id is not None
    assert facts[0].created_at is not None