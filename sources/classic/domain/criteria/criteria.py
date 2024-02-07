from typing import Any, Optional, Sequence

from .errors import CriteriaNotSatisfied


class Criteria:
    """
    Базовый класс для критериев.

    Нужен для описания критериев объектов, чтобы затем определять,
    соответствуют ли те или иные объекты критерию, или для формирования запроса,
    к примеру, в SQL-хранилище.

    Взят отсюда и доработано:
    https://gist.github.com/palankai/f73a18ce06751ab8f245

    Пример:
    >>> from datetime import datetime
    ... from dataclasses import dataclass
    ... from classic.domain import Criteria
    ...
    ... @dataclass
    ... class Task:
    ...     number: int
    ...     created_at: datetime
    ...     finished_at: datetime
    ...
    ... @dataclass
    ... class TaskOlderThan(Criteria):
    ...     date: datetime
    ...
    ...     def is_satisfied_by(self, task: Task) -> bool:
    ...         return self.date < task.created_at
    ...
    ... @dataclass
    ... class TaskObsolete(Criteria):
    ...     days_to_work: int
    ...
    ...     def is_satisfied_by(self, task: Task) -> bool:
    ...         days_spent = task.finished_at - task.created_at
    ...         return days_spent.days > self.days_to_work
    ...
    ... some_task = Task(
    ...     created_at=datetime(2024, 1, 1),
    ...     finished_at=datetime(2024, 1, 10),
    ... )
    ... old_and_obsolete = (
    ...     TaskObsolete(3) & TaskOlderThan(datetime(2024, 1, 31))
    ... )
    ... old_and_obsolete.is_satisfied_by(some_task)
    True

    >>> old_and_obsolete(some_task)
    True

    >>> list(filter(old_and_obsolete, [Task(1), Task(2), Task(3)]))
    Task(1)
    """

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __xor__(self, other):
        return Xor(self, other)

    def __invert__(self):
        return Invert(self)

    def is_satisfied_by(self, candidate: object) -> bool:
        raise NotImplementedError

    def __call__(self, candidate: object) -> bool:
        return self.is_satisfied_by(candidate)

    def must_be_satisfied_by(self, candidate: object) -> None:
        if not self.is_satisfied_by(candidate):
            raise CriteriaNotSatisfied

    def remainder_unsatisfied_by(
        self, candidate: object
    ) -> Optional['Criteria']:
        if self.is_satisfied_by(candidate):
            return None
        else:
            return self


class CompositeCriteria(Criteria):
    """
    Интерфейс критерия с неограниченным количеством вложенных критериев.

    Используется внутри библиотеки.
    """
    nested_criteria: Sequence[Criteria]

    def __init__(self, *criteria: Criteria):
        self.nested_criteria = list(criteria)

    def is_satisfied_by(self, candidate: object) -> bool:
        raise NotImplementedError


class And(CompositeCriteria):
    """
    Критерий, проверяющий, что все вложенные критерии удовлетворяются.

    Нужен для обработки логической операции И между несколькими критериями.
    В норме используется только под капотом и вручную не инстанцируется.
    """

    def __and__(self, other: Criteria):
        if isinstance(other, And):
            self.nested_criteria += other.nested_criteria
        else:
            self.nested_criteria += (other,)
        return self

    def is_satisfied_by(self, candidate: object):
        satisfied = all([
            criteria.is_satisfied_by(candidate)
            for criteria in self.nested_criteria
        ])
        return satisfied

    def remainder_unsatisfied_by(self, candidate: object):
        non_satisfied = [
            criteria
            for criteria in self.nested_criteria
            if not criteria.is_satisfied_by(candidate)
        ]
        if not non_satisfied:
            return None
        if len(non_satisfied) == 1:
            return non_satisfied[0]
        if len(non_satisfied) == len(self.nested_criteria):
            return self
        return And(*non_satisfied)


class Or(CompositeCriteria):
    """
    Критерий, проверяющий, что хотя бы один вложенный критерий удовлетворяются.

    Нужен для обработки логической операции ИЛИ между несколькими критериями.
    В норме используется только под капотом и вручную не инстанцируется.
    """

    def __or__(self, other):
        if isinstance(other, Or):
            self.nested_criteria += other.nested_criteria
        else:
            self.nested_criteria += (other,)
        return self

    def is_satisfied_by(self, candidate: object):
        satisfied = any([
            criteria.is_satisfied_by(candidate)
            for criteria in self.nested_criteria
        ])
        return satisfied


class UnaryCriteria(Criteria):
    """
    Интерфейс критерия с одним вложенным критерием.

    Используется внутри библиотеки.
    """
    nested_criteria: Criteria

    def __init__(self, criteria: Criteria):
        self.nested_criteria = criteria

    def is_satisfied_by(self, *args, **kwargs: Any) -> bool:
        raise NotImplementedError


class Invert(UnaryCriteria):
    """
    Критерий, проверяющий, что вложенный критерии не удовлетворяется.

    Нужен для обработки логической операции НЕ над вложенным критериями.
    В норме используется только под капотом и вручную не инстанцируется.
    """

    def is_satisfied_by(self, candidate: object):
        return not self.nested_criteria.is_satisfied_by(candidate)


class BinaryCriteria(Criteria):
    """
    Интерфейс критерия с двумя вложенными критериями.
    Нужен для реализации операций, в которых порядок элементов имеет значение.

    Используется внутри библиотеки.
    """
    left: Criteria
    right: Criteria

    def __init__(self, left: Criteria, right: Criteria):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: object) -> bool:
        raise NotImplementedError


class Xor(BinaryCriteria):
    """
    Критерий, проверяющий, что только один вложенный критерий удовлетворяется.

    Нужен для обработки логической операции ИСКЛЮЧАЮЩЕЕ ИЛИ
    над вложенными критериями. В норме используется
    только под капотом и вручную не инстанцируется.
    """

    def is_satisfied_by(self, candidate: object):
        return (
            self.left.is_satisfied_by(candidate) ^
            self.right.is_satisfied_by(candidate)
        )
