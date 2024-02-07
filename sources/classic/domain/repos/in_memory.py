from typing import Sequence

from classic.domain.criteria import Criteria

from .base import Persistent, Repo


class InMemoryRepo(Repo):

    def __init__(self):
        self.objects = {}

    def save(self, *objects: Persistent) -> None:
        for obj in objects:
            self.objects[obj.id] = obj

    def get(self, object_id: object) -> Persistent | None:
        return self.objects[object_id]

    def find(
        self, criteria: Criteria,
        order_by: str = None,
        limit: int = None,
        offset: int = None,
    ) -> Sequence[object]:
        return list(filter(criteria, self.objects))

    def remove(self, *objects: Persistent) -> None:
        for obj in objects:
            del self.objects[obj.id]

    def remove_by_id(self, *object_ids: object) -> None:
        for obj_id in object_ids:
            del self.objects[obj_id]

    def count(self, criteria: Criteria = None) -> int:
        return len(
            filter(criteria, self.objects)
            if criteria is not None
            else self.objects
        )

    def exists(self, criteria: Criteria) -> bool:
        return any(filter(criteria, self.objects))
