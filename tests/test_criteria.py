import pytest

from classic.criteria import CriteriaNotSatisfied

from .conftest import Entity, id_in


def test_simple(entity):
    assert entity.id_is(1)

    with (pytest.raises(CriteriaNotSatisfied)):
        criteria = Entity.id_is(2)
        criteria.must_be_satisfied(entity)


def test_filtering(collection):
    target = [1, 2, 3]
    criteria = id_in(target)

    assert list(filter(criteria, collection)) == [Enty]
