from abc import ABCMeta
from dataclasses import dataclass
from typing import Hashable, Generic, TypeVar


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


ID = TypeVar('ID', bound=Hashable)


class DomainObject:
    pass


@dataclass(eq=False)
class HaveID(Generic[ID]):
    id: ID


class Value(DomainObject, metaclass=ValueMeta):
    pass


class Entity(DomainObject, HaveID[ID], metaclass=EntityMeta):
    pass


class Root(Entity, HaveID[ID], metaclass=EntityMeta):
    pass
