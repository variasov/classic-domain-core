from typing import Any, Type, Callable, Sequence

from .criteria import Criteria


Predicate = Callable[[Any], bool]


class PredicateCriteria(Criteria):
    predicate: Predicate
    args: Sequence[object]
    kwargs: dict[str, object]

    def __init__(
        self, predicate: Predicate,
        *args: object, **kwargs: object,
    ) -> None:
        self.predicate = predicate
        self.args = args
        self.kwargs = kwargs

    def is_satisfied_by(self, candidate: object) -> bool:
        return self.predicate(candidate, *self.args, **self.kwargs)


class BoundPredicateCriteria:
    instance: object
    predicate: Predicate

    def __init__(self, instance: object, predicate: Predicate):
        self.instance = instance
        self.predicate = predicate

    def __call__(self, *args: object, **kwargs: object) -> bool:
        return self.is_satisfied(*args, **kwargs)

    def is_satisfied(self, *args: object, **kwargs: object) -> bool:
        criteria_ = PredicateCriteria(self.predicate, *args, **kwargs)
        return criteria_.is_satisfied_by(self.instance)

    def must_be_satisfied(self, *args: object, **kwargs: object) -> None:
        criteria_ = PredicateCriteria(self.predicate, *args, **kwargs)
        criteria_.must_be_satisfied_by(self.instance)


class PredicateCriteriaFactory:
    predicate: Predicate

    def __init__(self, predicate: Predicate):
        self.predicate = staticmethod(predicate)

    def __call__(self, *args: object, **kwargs: object) -> PredicateCriteria:
        return PredicateCriteria(self.predicate, *args, **kwargs)

    def __get__(
        self, instance: object, owner: type[object]
    ) -> PredicateCriteria | BoundPredicateCriteria:

        if instance:
            return BoundPredicateCriteria(instance, self.predicate)
        else:
            return self


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

    return PredicateCriteriaFactory(fn)

    # # Попытка отличить метод от функции.
    # # У методов в __qualname__ написан класс и название метода через точку,
    # # а у функций просто название, без точки
    # if '.' in fn.__qualname__:
    #     return CriteriaDescriptor(new_criteria)
