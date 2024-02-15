from copy import deepcopy
from typing import Sequence

from ..criteria import Criteria
from ..entities import ID, Root

from .base import Repo


class InMemoryRepo(Repo[Root, ID]):

    def __init__(self):
        self.objects = {}

    def save(self, *objects: Root) -> None:
        for obj in objects:
            self.objects[obj.id] = obj

    def get(self, object_id: ID) -> Root | None:
        return deepcopy(self.objects[object_id])

    def find(
        self, criteria: Criteria[Root],
        order_by: str = None,
        limit: int = None,
        offset: int = None,
    ) -> Sequence[object]:
        return list(filter(criteria, self.objects))

    def remove(self, *objects: Root) -> None:
        for obj in objects:
            del self.objects[obj.id]

    def remove_by_id(self, *object_ids: ID) -> None:
        for obj_id in object_ids:
            del self.objects[obj_id]

    def count(self, criteria: Criteria[Root] = None) -> int:
        return len(
            filter(criteria, self.objects.values())
            if criteria is not None
            else self.objects
        )

    def exists(self, criteria: Criteria[Root]) -> bool:
        return any(filter(criteria, self.objects.values()))
