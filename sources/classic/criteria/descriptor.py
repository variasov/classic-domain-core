import inspect
from functools import partial

from .criteria import Criteria


class CriteriaFactory:

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        return Criteria(self.fn,  *args, **kwargs)


class CriteriaDescriptor:

    def __init__(self, fn):
        self.factory = CriteriaFactory(fn)

        if len(inspect.signature(fn).parameters) == 1:
            self.factory = self.factory()

    @staticmethod
    def _call_fn(factory, instance, *args, **kwargs):
        criteria_ = factory(*args, **kwargs)
        return criteria_.is_satisfied_by(instance)

    def __get__(self, instance, owner):
        if instance:
            return partial(self._call_fn, self.factory, instance)
        else:
            return self.factory

    def __call__(self, *args, **kwargs):
        return self.factory(*args, **kwargs)


def criteria(fn):
    """
    Декоратор для удобного описания правила через функции:

    >>> from classic.criteria import criteria
    ...
    ... @criteria
    ... def is_author(user, book):
    ...     return user == book.author
    ...
    ... is_author(some_book).is_satisfied_by(some_user)
    False
    """
    return CriteriaDescriptor(fn)
