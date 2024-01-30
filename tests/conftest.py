import pytest

from classic.criteria import criteria, check_arg, check_result


class Entity:

    def __init__(self, id=None, value=None):
        self.id = id
        self.value = value

    @criteria
    def id_is(self, id_):
        return self.id == id_


@criteria
def id_in(entity, ids):
    return entity.id in ids


@pytest.fixture
def entity():
    return Entity(1)


@pytest.fixture
def collection():
    return [
        Entity(id_)
        for id_ in range(10)
    ]
