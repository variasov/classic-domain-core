from abc import ABCMeta
from dataclasses import dataclass
import inspect
from typing import Collection, get_origin, get_args, Hashable, ClassVar

from .criteria import Criteria, And, ReturnsTrue

from . import invariants


def descendants_invariants(cls):
    descendants: list[Criteria] = []
    for name, child_cls in inspect.get_annotations(cls).items():
        if isinstance(child_cls, (Value, Entity)):
            descendants.append(invariants.check_child(name))
            continue

        origin = get_origin(child_cls)
        if not origin:
            continue

        if isinstance(origin, dict):
            args = get_args(child_cls)
            if len(args) != 2:
                continue

            key_type, value_type = args
            key_is_domain = isinstance(key_type, (Value, Entity))
            value_is_domain = isinstance(value_type, (Value, Entity))

            if key_is_domain:
                if value_is_domain:
                    descendants.append(
                        invariants.check_child_dict_items(name)
                    )
                else:
                    descendants.append(
                        invariants.check_child_dict_keys(name)
                    )
            elif value_is_domain:
                descendants.append(
                    invariants.check_child_dict_values(name)
                )

        elif issubclass(origin, Collection):
            descendants.append(
                invariants.check_child_iterator(name)
            )

    return descendants


def build_invariants(cls) -> Criteria:
    cls_invariants = [
        invariant_() for __, invariant_
        in inspect.getmembers(cls, invariants.is_invariant)
    ] + descendants_invariants(cls)
    if cls_invariants:
        return And(*cls_invariants)
    else:
        return ReturnsTrue()


def fill_cls_invariants(cls, **kwargs):
    if not inspect.isabstract(cls):
        cls.invariants = build_invariants(cls)


class ValueMeta(ABCMeta):

    def __new__(mcs, *args, **kwargs):
        return dataclass(
            super().__new__(mcs, *args, **kwargs),
            frozen=True, eq=True, order=False,
        )


class EntityMeta(ABCMeta):

    def __new__(mcs, *args, **kwargs):
        return dataclass(
            super().__new__(mcs, *args, **kwargs),
            frozen=False, eq=False, order=False,
        )


class RootMeta(ABCMeta):

    def __new__(mcs, *args, **kwargs):
        return dataclass(
            super().__new__(mcs, *args, **kwargs),
            frozen=False, eq=False, order=False,
        )


class DomainObject:
    """
    Базовый класс для всех доменных объектов.
    """

    invariants: ClassVar[Criteria]


class Value(DomainObject, metaclass=ValueMeta):

    __init_subclass__ = fill_cls_invariants


class Entity(DomainObject, metaclass=EntityMeta):
    id: Hashable

    __init_subclass__ = fill_cls_invariants


class Root(DomainObject, metaclass=RootMeta):
    id: Hashable

    __init_subclass__ = fill_cls_invariants
