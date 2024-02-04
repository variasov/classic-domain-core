from dataclasses import make_dataclass, asdict, dataclass
import inspect
from typing import Type, Callable, cast

from .criteria import Criteria


Predicate = Callable[[...], bool]


class PredicateCriteria(Criteria):
    predicate: Predicate

    def __init__(self, *args, **kwargs):
        pass


def call_predicate(criteria_: PredicateCriteria, candidate: object) -> bool:
    return criteria_.predicate(candidate, **asdict(criteria_))


def make_predicate_criteria(fn: Predicate) -> (
    Type[PredicateCriteria] | PredicateCriteria
):
    signature = inspect.signature(fn)
    params = [
        (param.name, param.annotation)
        for param in list(signature.parameters.values())[1:]
    ]
    cls = make_dataclass(
        fn.__name__,
        params,
        bases=(Criteria,),
        namespace={
            'predicate': staticmethod(fn),
            'is_satisfied_by': call_predicate,
        }
    )
    if not params:
        return cls()

    return cast(Type[PredicateCriteria], cls)


@dataclass(frozen=True, slots=True, eq=False)
class CriteriaCall:
    instance: object
    criteria_cls: Type[PredicateCriteria]

    def __call__(self, *args: object, **kwargs: object) -> bool:
        criteria_ = self.criteria_cls(*args, **kwargs)
        return criteria_.is_satisfied_by(self.instance)


@dataclass(frozen=True, slots=True, eq=False)
class CriteriaDescriptor:
    criteria_cls: Type[PredicateCriteria] | Criteria

    def __get__(
        self, instance: object,
        owner: Type[object],
    ) -> CriteriaCall | Type[Criteria] | Criteria:
        if instance:
            return CriteriaCall(instance, self.criteria_cls)
        else:
            return self.criteria_cls


def method_criteria(
    fn
) -> CriteriaDescriptor | Type[PredicateCriteria] | PredicateCriteria:
    """
    Декоратор для удобного описания правила через функции:

    >>> from dataclasses import dataclass
    ... from classic.criteria import method_criteria
    ...
    ... @dataclass
    ... class Book:
    ...     author: str
    ...
    ...     @method_criteria
    ...     def can_edit(self, user: str) -> bool:
    ...         return self.author == user
    ...
    ... some_book = Book('Ivan')
    ... Book.can_edit('Ivan').is_satisfied_by(some_book)
    True
    >>> some_book.can_edit('Ivan')
    True
    """
    return CriteriaDescriptor(make_predicate_criteria(fn))


def func_criteria(
    fn
) -> Type[PredicateCriteria] | PredicateCriteria:
    """
    Декоратор для удобного описания правила через функции:

    >>> from dataclasses import dataclass
    ... from classic.criteria import func_criteria
    ...
    ... @dataclass
    ... class Book:
    ...     author: str
    ...
    ... @func_criteria
    ... def can_edit_book(book, user: str) -> bool:
    ...     return book.author == user
    ...
    ... some_book = Book('Ivan')
    ... can_edit_book('Ivan').is_satisfied_by(some_book)
    True
    """
    return make_predicate_criteria(fn)
