from functools import wraps
import inspect

from classic.components import doublewrap

from .criteria import Criteria


_EMPTY = object()


@doublewrap
def check_arg(fn, prop: str, criteria: Criteria, skip: bool = False):
    """
    Декоратор, проверяющий указанные аргумент на соответствие критерию
    при вызове декорируемой функции.

    >>> from classic.criteria import criteria, check_arg
    ...
    ... @criteria
    ... def is_authenticated(identity):
    ...     return identity is not None
    ...
    ... @check_arg('identity', is_authenticated)
    ... def some_method(identity, book_id):
    ...     pass
    ...
    ... some_method(identity=1)
    True
    """

    signature = inspect.signature(fn)

    @wraps(fn)
    def wrapper(*args, **kwargs):
        candidate = signature.bind(args, kwargs).arguments[prop]

        if skip and not criteria.is_satisfied_by(candidate):
            return None
        else:
            criteria.must_be_satisfied(candidate)

        return fn(*args, **kwargs)

    return wrapper


@doublewrap
def check_result(fn, criteria: Criteria, skip: bool = False):
    """
    Декоратор, проверяющий результат функции на соответствие заданному критерию.

    >>> from classic.criteria import criteria, check_result
    ...
    ... @criteria
    ... def is_none(value):
    ...     return value is not None
    ...
    ... @check_result(is_none)
    ... def returns(identity):
    ...     return 1
    ...
    ... @check_result(is_none)
    ... def return_none(identity):
    ...     return None
    ...
    ... returns(1)
    1
    >>> return_none()
    CriteriaNotSatisfied
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)

        if skip and not criteria.is_satisfied_by(result):
            return None
        else:
            criteria.must_be_satisfied(result)

        return result

    return wrapper
