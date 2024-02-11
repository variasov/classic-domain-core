import pytest

from classic.domain.core import criteria, CriteriaNotSatisfied


class Entity:

    def __init__(self, value):
        self.value = value

    @criteria
    def with_param(self, value):
        return self.value == value

    @criteria
    def without_param(self):
        return self.value is not None

    rule = without_param() & with_param(1)


@criteria
def with_param(entity, value):
    return entity.value == value


@criteria
def without_param(entity):
    return entity.value is not None


@pytest.fixture
def entity():
    return Entity(1)


def test_instance(entity):
    assert entity.with_param(1) is True
    assert entity.with_param.is_satisfied(1) is True
    assert entity.with_param.must_be_satisfied(1) is None

    assert entity.without_param() is True
    assert entity.without_param.is_satisfied() is True
    assert entity.without_param.must_be_satisfied() is None

    assert entity.rule() is True
    assert entity.rule.is_satisfied() is True
    assert entity.rule.must_be_satisfied() is None

    with pytest.raises(CriteriaNotSatisfied):
        entity.with_param.must_be_satisfied(2)


@pytest.mark.parametrize('criteria_', (
    Entity.with_param(1),
    Entity.with_param(1) & Entity.without_param(),
    Entity.with_param(1) & Entity.without_param() & with_param(1),
    Entity.with_param(1) & Entity.without_param() & with_param(1) & without_param(),
    Entity.with_param(1) & Entity.without_param() & with_param(1) & without_param() & Entity.rule,
))
def test_class_criteria(criteria_, entity):
    assert criteria_(entity) is True
    assert criteria_.is_satisfied_by(entity) is True
    criteria_.must_be_satisfied_by(entity)


def test_method_without_params(entity):
    assert entity.without_param() is True

    with pytest.raises(CriteriaNotSatisfied):
        Entity.without_param().must_be_satisfied_by(Entity(None))
