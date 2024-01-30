from typing import Any, Optional

from .errors import CriteriaNotSatisfied


class Criteria:
    """
    Базовый объект-критерий.

    Нужен для описания критериев объектов, чтобы затем определять,
    соответствуют ли те или иные объекты критерию, или для формирования запроса,
    к примеру, в SQL-хранилище.

    Взят отсюда и чуть-чуть доработано:
    https://gist.github.com/palankai/f73a18ce06751ab8f245

    Пример:
    >>> from datetime import datetime
    ... from dataclasses import dataclass
    ... from classic.criteria import Criteria
    ...
    ... @dataclass
    ... class Task:
    ...     created_at: datetime
    ...     finished_at: datetime
    ...
    ... @dataclass
    ... class TaskOlderThan(Criteria):
    ...     date: datetime
    ...
    ...     def is_satisfied_by(self, candidate: Task) -> bool:
    ...         return candidate.created_at < self.date
    ...
    ... @dataclass
    ... class TaskObsolete(Criteria):
    ...     days_to_work: int
    ...
    ...     def is_satisfied_by(self, candidate: Task) -> bool:
    ...         days_spent = candidate.finished_at - candidate.created_at
    ...         return days_spent.days > self.days_to_work
    ...
    ... some_task = Task(
    ...     created_at=datetime(2024, 1, 1),
    ...     finished_at=datetime(2024, 1, 10),
    ... )
    ... criteria = TaskObsolete(3) & TaskOlderThan(datetime(2024, 1, 31))
    ... criteria.is_satisfied_by(some_task)
    True
    >>> some_task = Task(
    ...     created_at=datetime(2024, 1, 1),
    ...     finished_at=datetime(2024, 1, 1),
    ... )
    ... criteria = TaskObsolete(3) & TaskOlderThan(datetime(2024, 1, 31))
    ... criteria.is_satisfied_by(some_task)
    False
    """

    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __xor__(self, other):
        return Xor(self, other)

    def __invert__(self):
        return Invert(self)

    def is_satisfied_by(self, candidate: object) -> bool:
        return self.fn(candidate, *self.args, **self.kwargs)

    def __call__(self, candidate: object) -> bool:
        return self.is_satisfied_by(candidate)

    def must_be_satisfied(self, candidate: object) -> None:
        if not self.is_satisfied_by(candidate):
            raise CriteriaNotSatisfied

    def remainder_unsatisfied_by(
        self, *args: Any, **kwargs: Any
    ) -> Optional['Criteria']:
        if self.is_satisfied_by(*args, **kwargs):
            return None
        else:
            return self


class CompositeCriteria(Criteria):

    def __init__(self, *criteria: Criteria):
        self.criteria = criteria

    def is_satisfied_by(self, candidate: object) -> bool:
        raise NotImplementedError


class And(CompositeCriteria):

    def __and__(self, other: Criteria):
        if isinstance(other, And):
            self.criteria += other.criteria
        else:
            self.criteria += (other,)
        return self

    def is_satisfied_by(self, candidate: object):
        satisfied = all([
            criteria.is_satisfied_by(candidate)
            for criteria in self.criteria
        ])
        return satisfied

    def remainder_unsatisfied_by(self, candidate: object):
        non_satisfied = [
            criteria
            for criteria in self.criteria
            if not criteria.is_satisfied_by(candidate)
        ]
        if not non_satisfied:
            return None
        if len(non_satisfied) == 1:
            return non_satisfied[0]
        if len(non_satisfied) == len(self.criteria):
            return self
        return And(*non_satisfied)


class Or(CompositeCriteria):

    def __or__(self, other):
        if isinstance(other, Or):
            self.criteria += other.criteria
        else:
            self.criteria += (other,)
        return self

    def is_satisfied_by(self, candidate: object):
        satisfied = any([
            criteria.is_satisfied_by(candidate)
            for criteria in self.criteria
        ])
        return satisfied


class NestedCriteria(Criteria):

    def __init__(self, criteria: Criteria):
        self.criteria = criteria

    def is_satisfied_by(self, *args, **kwargs: Any) -> bool:
        raise NotImplementedError


class Invert(NestedCriteria):

    def is_satisfied_by(self, candidate: object):
        return not self.criteria.is_satisfied_by(candidate)


class BinaryCriteria(Criteria):

    def __init__(self, left: Criteria, right: Criteria):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: object) -> bool:
        raise NotImplementedError


class Xor(BinaryCriteria):

    def is_satisfied_by(self, candidate: object):
        return (
            self.left.is_satisfied_by(candidate) ^
            self.right.is_satisfied_by(candidate)
        )

