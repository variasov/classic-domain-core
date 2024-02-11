from typing import (
    ClassVar, Type, Sequence, Generic,
    TypeVar, get_args, Callable,
)

from ..criteria import Criteria
from .. import entities

from .translate import translators_map


Root = TypeVar('Root', bound=entities.Root)


class Repo(Generic[Root]):
    root: type[Root] = None
    _translators: ClassVar[dict[Type[Criteria], Callable]]

    def __init_subclass__(cls, **kwargs: object):
        cls._translators = translators_map(cls)
        try:
            root = get_args(cls)[0]
        except IndexError:
            pass
        else:
            if issubclass(root, entities.Root):
                cls.root = root

    def save(self, *objects: Root) -> None:
        raise NotImplemented

    def get(self, id_) -> Root | None:
        raise NotImplemented

    def find(
        self, criteria: Criteria,
        order_by: str = None,
        limit: int = None,
        offset: int = None,
    ) -> Sequence[Root]:
        raise NotImplemented

    def count(self, criteria: Criteria = None) -> int:
        raise NotImplemented

    def exists(self, criteria: Criteria) -> bool:
        raise NotImplemented

    def remove(self, *objects: Root) -> None:
        raise NotImplemented

    def remove_by_id(self, *object_ids: object) -> None:
        raise NotImplemented
