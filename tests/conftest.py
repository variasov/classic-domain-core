import pytest

from classic.domain.criteria import criteria


class Entity:

    def __init__(self, id=None, value=None):
        self.id = id
        self.value = value

    @criteria
    def id_is(self, id_):
        return self.id == id_

    @criteria
    def have_id(self):
        return self.id is not None


@criteria
def id_in(entity, ids):
    return entity.id in ids


@criteria
def is_entity(entity):
    return isinstance(entity, Entity)


@pytest.fixture
def entity():
    return Entity(1)


@pytest.fixture
def collection():
    return [
        Entity(id_)
        for id_ in range(10)
    ]
