from typing import Generic, Optional, Self, TypeVar, get_args, Type


Entity = TypeVar('Entity')


class Criteria(Generic[Entity]):
    """
    Базовый объект-критерий.

    Нужен для описания критериев объектов, чтобы затем определять,
    соответствуют ли те или иные объекты критерию, или для формирования запроса,
    к примеру, в SQL-хранилище.

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
    ... class TaskOlderThan(Criteria[Task]):
    ...     date: datetime
    ...
    ...     def is_satisfied_by(self, candidate: Task) -> bool:
    ...         return candidate.created_at < self.date
    ...
    ... @dataclass
    ... class TaskObsolete(Criteria[Task]):
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

    @property
    def entity_cls(self) -> Type[object]:
        args = get_args(self)
        if len(args) >= 0:
            return args[0]

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __xor__(self, other):
        return Xor(self, other)

    def __invert__(self):
        return Invert(self)

    def is_satisfied_by(self, candidate: Entity) -> bool:
        raise NotImplemented

    def remainder_unsatisfied_by(self, candidate: Entity) -> Optional[Self]:
        if self.is_satisfied_by(candidate):
            return None
        else:
            return self


class BoundCriteria(Criteria[Entity]):

    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def is_satisfied_by(self, candidate: Entity) -> bool:
        assert isinstance(candidate, self.entity_cls)
        return self.fn(candidate, *self.args, **self.kwargs)


class CompositeCriteria(Criteria[Entity]):

    def __init__(self, *criteria: Criteria[Entity]):
        self.criteria = criteria

    def is_satisfied_by(self, candidate: Entity) -> bool:
        raise NotImplementedError


class And(CompositeCriteria):

    def __and__(self, other: Criteria[Entity]):
        if isinstance(other, And):
            self.criteria += other.criteria
        else:
            self.criteria += (other,)
        return self

    def is_satisfied_by(self, candidate: Entity):
        satisfied = all([
            criteria.is_satisfied_by(candidate)
            for criteria in self.criteria
        ])
        return satisfied

    def remainder_unsatisfied_by(self, candidate: Entity):
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

    def is_satisfied_by(self, candidate: Entity):
        satisfied = any([
            criteria.is_satisfied_by(candidate)
            for criteria in self.criteria
        ])
        return satisfied


class NestedCriteria(Criteria[Entity]):

    def __init__(self, criteria: Criteria[Entity]):
        self.criteria = criteria

    def is_satisfied_by(self, candidate: Entity) -> bool:
        raise NotImplementedError


class Invert(NestedCriteria):

    def is_satisfied_by(self, candidate: Entity):
        return not self.criteria.is_satisfied_by(candidate)


class BinaryCriteria(Criteria[Entity]):

    def __init__(self, left: Criteria[Entity], right: Criteria[Entity]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Entity) -> bool:
        raise NotImplementedError


class Xor(BinaryCriteria[Entity]):

    def is_satisfied_by(self, candidate: Entity):
        return (
            self.left.is_satisfied_by(candidate) ^
            self.right.is_satisfied_by(candidate)
        )
