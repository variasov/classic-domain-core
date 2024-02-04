import pytest

from classic.criteria import CriteriaNotSatisfied

from .conftest import Entity, id_in, is_entity


def test_method(entity):
    assert entity.id_is(1)

    with pytest.raises(CriteriaNotSatisfied):
        Entity.id_is(2).must_be_satisfied_by(entity)


def test_method_without_params(entity):
    assert entity.have_id

    with pytest.raises(CriteriaNotSatisfied):
        Entity.have_id.must_be_satisfied_by(Entity())


def test_func_without_params(entity):
    assert is_entity(entity)
    assert not is_entity(1)
    assert (is_entity & id_in([1])).is_satisfied_by(entity)


def test_func(collection):
    target = [1, 2, 3]
    criteria = id_in(target)

    assert list(filter(criteria, collection)) == [
        collection[1], collection[2], collection[3],
    ]
