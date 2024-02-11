from typing import Type, Callable, Sequence, cast

from .criteria import Criteria, CriteriaDescriptor, BoundUnformedCriteria


Predicate = Callable[[object, ...], bool]


class PredicateCriteria(Criteria):
    predicate: Predicate
    args: Sequence[object]
    kwargs: dict[str, object]

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.args = args
        self.kwargs = kwargs

    def is_satisfied_by(self, candidate: object) -> bool:
        return self.predicate(candidate, *self.args, **self.kwargs)

    def __str_(self) -> str:
        return self.predicate.__name__


def make_predicate_criteria(fn: Predicate) -> Type[PredicateCriteria]:
    new_cls = type(
        fn.__name__,
        (PredicateCriteria,),
        {
            'predicate': staticmethod(fn),
            '__is_invariant__': getattr(fn, '__is_invariant__', False),
        }
    )
    return cast(Type[PredicateCriteria], new_cls)


def criteria(
    fn
) -> PredicateCriteria | BoundUnformedCriteria:
    """
    Декоратор для удобного описания правила через функции:

    Пример:
    >>> from dataclasses import dataclass
    ... from classic.domain.core import criteria
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
    ... from classic.domain.core import criteria
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

    return CriteriaDescriptor(
        make_predicate_criteria(fn)
    )
