from dataclasses import asdict
from typing import Any, Type, Callable, Sequence, cast

from .criteria import Criteria


Predicate = Callable[[Any], bool]


class PredicateCriteria(Criteria):
    predicate: Predicate
    args: Sequence[object]
    kwargs: dict[str, object]

    def __init__(
        self,
        *args: object, **kwargs: object,
    ) -> None:
        self.args = args
        self.kwargs = kwargs

    def is_satisfied_by(self, candidate: object) -> bool:
        return self.predicate(candidate, *self.args, **self.kwargs)

    def __str_(self):
        return self.predicate.__name__


def call_predicate(criteria_: PredicateCriteria, candidate: object) -> bool:
    return criteria_.predicate(candidate, **asdict(criteria_))


def make_predicate_criteria(fn: Predicate) -> (
    Type[PredicateCriteria] | PredicateCriteria
):
    new_cls = type(
        fn.__name__,
        (PredicateCriteria,),
        {
            'predicate': staticmethod(fn),
            '__is_invariant__': getattr(fn, '__is_invariant__', False),
        }
    )
    return cast(Type[PredicateCriteria], new_cls)


class BoundPredicateCriteria:
    instance: object
    criteria_cls: type[PredicateCriteria]

    def __init__(self, instance: object, criteria_cls: type[PredicateCriteria]):
        self.instance = instance
        self.criteria_cls = criteria_cls

    def __call__(self, *args: object, **kwargs: object) -> bool:
        return self.is_satisfied(*args, **kwargs)

    def is_satisfied(self, *args: object, **kwargs: object) -> bool:
        return self.criteria_cls(*args, **kwargs).is_satisfied_by(self.instance)

    def must_be_satisfied(self, *args: object, **kwargs: object) -> None:
        self.criteria_cls(*args, **kwargs).must_be_satisfied_by(self.instance)


class PredicateCriteriaFactory:
    criteria_cls: type[PredicateCriteria]

    def __init__(self, criteria_cls: type[PredicateCriteria]):
        self.criteria_cls = criteria_cls

    def __call__(self, *args: object, **kwargs: object) -> PredicateCriteria:
        return self.criteria_cls(*args, **kwargs)

    def __get__(
        self, instance: object, owner: type[object]
    ) -> PredicateCriteria | BoundPredicateCriteria:

        if instance:
            return BoundPredicateCriteria(instance, self.criteria_cls)
        else:
            return self.criteria_cls


def criteria(
    fn
) -> Type[PredicateCriteria] | PredicateCriteria:
    """
    Декоратор для удобного описания правила через функции:

    Пример:
    >>> from dataclasses import dataclass
    ... from classic.domain import criteria
    ...
    ... @dataclass
    ... class Book:
    ...     author: str
    ...
    ... @criteria
    ... def can_edit_book(book, user):
    ...     return book.author == user
    ...
    ... some_book = Book('Ivan')
    ... can_edit_book('Ivan').is_satisfied_by(some_book)
    True

    Также можно оборачивать методы в классе:
    >>> from dataclasses import dataclass
    ... from classic.domain import criteria
    ...
    ... @dataclass
    ... class Book:
    ...     author: str
    ...
    ...     @criteria
    ...     def can_edit(self, user):
    ...         return self.author == user
    ...
    ... some_book = Book('Ivan')
    ... Book.can_edit('Ivan').is_satisfied_by(some_book)
    True
    >>> some_book.can_edit('Ivan')
    True
    """
    assert callable(fn)

    return PredicateCriteriaFactory(
        make_predicate_criteria(fn)
    )

    # # Попытка отличить метод от функции.
    # # У методов в __qualname__ написан класс и название метода через точку,
    # # а у функций просто название, без точки
    # if '.' in fn.__qualname__:
    #     return CriteriaDescriptor(new_criteria)
