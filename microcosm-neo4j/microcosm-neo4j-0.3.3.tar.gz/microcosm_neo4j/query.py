"""
Query API.

"""
from contextlib import contextmanager
from typing import Dict, Generator, List

from neo4j import BoltStatementResult, Record, Session
from neobolt.exceptions import ConstraintError
from opencypher.ast import Cypher

from microcosm_neo4j.errors import DuplicateModelError, ModelIntegrityError, NotFoundError


@contextmanager
def error_handling() -> Generator[None, None, None]:
    """
    Handle common Neo4J errors and re-raise as typed exceptions.

    Many Neo4J errors are only differentiable via error message text; handle all of this
    logic in one place.

    """
    try:
        yield
    except ConstraintError as error:
        if "already exists" in error.message:
            raise DuplicateModelError(error)
        if "due to conflicts with existing unique nodes" in error.message:
            raise DuplicateModelError(error)
        raise ModelIntegrityError(error)


def run(session: Session, query: Cypher) -> BoltStatementResult:
    """
    Run a query using the current session.

    """
    # express the query as a string
    cypher = str(query)
    # express the parameters as a dictionary
    parameters = dict(query)
    return session.run(cypher, **parameters)


def to_dict(record: Record) -> Dict[str, str]:
    """
    Convert a return value into a dictionary.

    Note that while the `_id` property is accessible during this translation,
    we choose to respect Neo4J's design that its internal integer ids be treated
    as implementation details.

    """
    # NB: assumes we only want one record at a time; for more complex cases use `record[variable]`
    entity = next(iter(record))
    return entity._properties


def one_record(session: Session, query: Cypher) -> Dict[str, str]:
    with error_handling():
        record = run(session, query).single()

    if record is None:
        # Neo4J doesn't give us a lot of context in its error responses; however just about
        # every reason we might not get back a result relates to either omitting a `RETURN`
        # clause or defining `MATCH` clause with no results.
        raise NotFoundError()

    return to_dict(record)


def all_records(session: Session, query: Cypher) -> List[Dict[str, str]]:
    with error_handling():
        return [
            to_dict(record)
            for record in run(session, query)
        ]
