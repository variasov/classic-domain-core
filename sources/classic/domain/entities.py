from dataclasses import dataclass
import inspect
from typing import Collection, get_origin, get_args, TypeVar

from classic.domain import And

from .criteria import Criteria, criteria


method = TypeVar('method')


def invariant(fn: method) -> method:
    fn.__is_invariant__ = True
    return criteria(fn)


def is_invariant(obj: object) -> bool:
    return hasattr(obj, '__is_invariant__')


@invariant
def check_child_invariants(instance: object, child_name: str):
    return getattr(instance, child_name).all_invariants


@invariant
def check_child_iterator_invariants(instance: object, child_name: str):
    return all(
        item.all_invariants
        for item in getattr(instance, child_name)
    )


@invariant
def check_child_dict_items_invariants(instance: object, child_name: str):
    return all(
        key.all_invariants and value.all_invariants
        for key, value in getattr(instance, child_name).items()
    )


@invariant
def check_child_dict_values_invariants(instance: object, child_name: str):
    return all(
        item.all_invariants
        for item in getattr(instance, child_name).values()
    )


@invariant
def check_child_dict_keys_invariants(instance: object, child_name: str):
    return all(
        item.all_invariants
        for item in getattr(instance, child_name).keys()
    )


def child_invariants(cls):
    childs: list[Criteria] = []
    for name, child_cls in inspect.get_annotations(cls).items():
        if (
            (is_entity(child_cls) or is_value_object(child_cls)) and
            hasattr(child_cls, 'all_invariants')
        ):
            childs.append(check_child_invariants(name))
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
                    childs.append(
                        check_child_dict_items_invariants(name)
                    )
                else:
                    childs.append(
                        check_child_dict_keys_invariants(name)
                    )
            elif value_is_domain:
                childs.append(
                    check_child_dict_values_invariants(name)
                )

        elif issubclass(origin, Collection):
            childs.append(
                check_child_iterator_invariants(name)
            )

    return And(*childs)


def get_all_invariants(cls):
    return And(*(
        invariant_ for __, invariant_
        in inspect.getmembers(cls, is_invariant)
    )) & child_invariants(cls)


Class = TypeVar('Class')


def value_object(cls: Class) -> Class:
    cls.all_invariants = get_all_invariants(cls)
    cls.__domain_object__ = value_object
    return dataclass(cls, frozen=True, eq=True, order=False)


def entity(cls: Class) -> Class:
    cls.all_invariants = get_all_invariants(cls)
    cls.__domain_object__ = entity
    return dataclass(cls)


def root(cls: Class) -> Class:
    cls.all_invariants = get_all_invariants(cls)
    cls.__domain_object__ = root
    return dataclass(cls)


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
