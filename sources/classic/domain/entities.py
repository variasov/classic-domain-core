from dataclasses import dataclass
import inspect
from typing import Collection, get_origin, get_args, TypeVar

from classic.domain import And

from .criteria import Criteria, ReturnsTrue

from . import invariants


def descendants_invariants(cls):
    descendants: list[Criteria] = []
    for name, child_cls in inspect.get_annotations(cls).items():
        if is_entity(child_cls) or is_value_object(child_cls):
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
            key_is_domain = is_entity(key_type) or is_value_object(key_type)
            value_is_domain = (
                is_entity(value_type) or
                is_value_object(value_type)
            )
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


Class = TypeVar('Class', bound=type[object])


def value_object(cls: Class) -> Class:
    cls.__invariants__ = build_invariants(cls)
    cls.__domain_object__ = value_object
    return dataclass(cls, frozen=True, eq=True, order=False)


def entity(cls: Class) -> Class:
    cls.__invariants__ = build_invariants(cls)
    cls.__domain_object__ = entity
    return dataclass(cls)


def root(cls: Class) -> Class:
    cls.__invariants__ = build_invariants(cls)
    cls.__domain_object__ = root
    return dataclass(cls)


def all_invariants(cls: Class) -> Criteria:
    return cls.__invariants__


def is_domain_object(obj: object) -> bool:
    return isinstance(obj, type) and hasattr(obj, '__domain_object__')


def is_value_object(obj: object) -> bool:
    return (
        isinstance(obj, type) and
        getattr(obj, '__domain_object__', None) is value_object
    )


def is_entity(obj: object) -> bool:
    return (
        isinstance(obj, type) and
        getattr(obj, '__domain_object__', None) in (entity, root)
    )


def is_root(obj: object) -> bool:
    return (
        isinstance(obj, type) and
        getattr(obj, '__domain_object__', None) is root
    )
