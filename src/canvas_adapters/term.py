from typing import TypedDict, Optional
import datetime
import functools

from .dictionary_adapter import DictAdapter


class TermDict(TypedDict):
    id: int
    name: str
    start_at: str
    end_at: str
    created_at: str
    workflow_state: str
    grading_period_group_id: str


@functools.total_ordering
class Term(DictAdapter):
    id: int
    name: str
    start_at: Optional[datetime.datetime]
    end_at: Optional[datetime.datetime]
    created_at: Optional[datetime.datetime]
    workflow_state: str
    grading_period_group_id: Optional[str]

    def __init__(self, canvas_term: TermDict):
        super().__init__(canvas_term)
        # transform any of the dates into datetime objects
        for member, value in canvas_term.items():
            if member.endswith('_at'):
                value = datetime.datetime.fromisoformat(value.rstrip('Z')) if value is not None else None
                setattr(self, member, value)

    def __lt__(self, other: "Term") -> bool:
        if not isinstance(other, Term):
            raise NotImplemented(f'Inequality between {type(self)} and {type(other)} is note defined')
        if self.start_at is not None and other.start_at is not None:
            return self.start_at < other.start_at
        else:
            return self.created_at < other.created_at
