import inspect
from typing import Type, Callable

from classic.components import doublewrap

from ..criteria import Criteria


def is_translator(obj: object) -> bool:
    return callable(obj) and hasattr(obj, '__criteria__')


@doublewrap
def translate_for(fn, criteria: Type[Criteria]):
    assert issubclass(criteria, Criteria)

    fn.__criteria__ = criteria
    return fn


def translators_map(cls: Type[object]) -> dict[Type[Criteria], Callable]:
    return {
        method.__criteria__: method
        for __, method
        in inspect.getmembers(cls, is_translator)
    }
