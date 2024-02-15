import inspect
from typing import Collection, get_origin, get_args, ClassVar, TypeVar

from .entities import Value, Entity
from .criteria import Criteria, And, ReturnsTrue
from .predicate_wrapping import criteria


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


CHECKABLE = Value, Entity


def descendants_invariants(cls):
    descendants: list[Criteria] = []
    for name, child_cls in inspect.get_annotations(cls).items():
        if isinstance(child_cls, CHECKABLE):
            descendants.append(check_child(name))
            continue

        origin = get_origin(child_cls)
        if not origin:
            continue

        if isinstance(origin, dict):
            args = get_args(child_cls)
            if len(args) != 2:
                continue

            key_type, value_type = args
            key_is_domain = isinstance(key_type, CHECKABLE)
            value_is_domain = isinstance(value_type, CHECKABLE)

            if key_is_domain:
                if value_is_domain:
                    descendants.append(
                        check_child_dict_items(name)
                    )
                else:
                    descendants.append(
                        check_child_dict_keys(name)
                    )
            elif value_is_domain:
                descendants.append(
                    check_child_dict_values(name)
                )

        elif issubclass(origin, Collection):
            descendants.append(
                check_child_iterator(name)
            )

    return descendants


def build_invariants(cls) -> Criteria:
    cls_invariants = [
        invariant_() for __, invariant_
        in inspect.getmembers(cls, is_invariant)
    ] + descendants_invariants(cls)
    if cls_invariants:
        return And(*cls_invariants)
    else:
        return ReturnsTrue()


class HaveInvariants:
    """
    Базовый класс для всех доменных объектов.
    """

    invariants: ClassVar[Criteria]

    def __init_subclass__(cls, **kwargs):
        if not inspect.isabstract(cls):
            cls.invariants = build_invariants(cls)
