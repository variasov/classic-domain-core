from typing import TypeVar

from .criteria import criteria


Function = TypeVar('Function')


def invariant(fn: Function) -> Function:
    fn.__is_invariant__ = True
    fn = criteria(fn)
    return fn


def is_invariant(obj: object) -> bool:
    return (
        getattr(obj, '__is_invariant__', False) or
        getattr(getattr(obj, 'predicate', None), '__is_invariant__', False)
    )


@criteria
def check_child(instance: object, child_name: str):
    return getattr(instance, child_name).invariants.is_satisfied()


@criteria
def check_child_iterator(instance: object, child_name: str):
    return all(
        item.invariants.is_satisfied()
        for item in getattr(instance, child_name)
    )


@criteria
def check_child_dict_items(instance: object, child_name: str):
    return all(
        key.invariants.is_satisfied() and
        value.invariants.is_satisfied()
        for key, value in getattr(instance, child_name).items()
    )


@criteria
def check_child_dict_values(instance: object, child_name: str):
    return all(
        item.invariants.is_satisfied()
        for item in getattr(instance, child_name).values()
    )


@criteria
def check_child_dict_keys(instance: object, child_name: str):
    return all(
        item.invariants.is_satisfied()
        for item in getattr(instance, child_name).keys()
    )
