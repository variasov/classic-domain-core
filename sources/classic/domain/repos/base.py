from typing import (
    ClassVar, Type, Sequence, Generic,
    TypeVar, get_args, Callable,
)

from classic.domain.criteria import Criteria

from .translate import translators_map


Persistent = TypeVar('Persistent')


class Repo(Generic[Persistent]):
    persistent_cls: Type[Persistent] = None
    _translators: ClassVar[dict[Type[Criteria], Callable]]

    def __init_subclass__(cls, **kwargs: object):
        cls._translators = translators_map(cls)
        try:
            cls.persistent_cls = get_args(cls)[0]
        except IndexError:
            pass

    def save(self, *objects: Persistent) -> None:
        raise NotImplemented

    def get(self, id_) -> Persistent | None:
        raise NotImplemented

    def find(
        self, criteria: Criteria,
        order_by: str = None,
        limit: int = None,
        offset: int = None,
    ) -> Sequence[Persistent]:
        raise NotImplemented

    def count(self, criteria: Criteria = None) -> int:
        raise NotImplemented

    def exists(self, criteria: Criteria) -> bool:
        raise NotImplemented

    def remove(self, *objects: Persistent) -> None:
        raise NotImplemented

    def remove_by_id(self, *object_ids: object) -> None:
        raise NotImplemented
