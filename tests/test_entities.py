from dataclasses import field

import pytest

from classic.domain import (
    entity, value_obj, root, invariant, CriteriaNotSatisfied
)


class Base:
    int_field: int
    str_field: str

    @invariant
    def check_int_field(self):
        return isinstance(self.int_field, int)

    @invariant
    def check_str_field(self):
        return isinstance(self.str_field, str)


@value_obj
class SomeValue(Base):
    __annotations__ = Base.__annotations__


@entity
class SomeEntity(Base):
    __annotations__ = Base.__annotations__
    id: int


@root
class SomeRoot(Base):
    __annotations__ = Base.__annotations__
    id: int
    child: list[SomeEntity] = field(default_factory=list)


@pytest.mark.parametrize('instance,value', (
    (SomeValue(123, 'value'), True),
    (SomeValue(None, 'value'), False),
    (SomeValue(123, None), False),
    (SomeValue(None, None), False),
    (SomeEntity(123, 'value', 1), True),
    (SomeRoot(123, 'value', 1, child=[
        SomeEntity(123, 'value', 1),
        SomeEntity(123, 'value', 2),
    ]), True),
))
def test_invariants_on_value(instance, value):
    cls = instance.__class__

    assert cls.__invariants__.is_satisfied_by(instance) is value
    assert instance.__invariants__() is value
    assert instance.__invariants__.is_satisfied() is value

    if not value:
        with pytest.raises(CriteriaNotSatisfied):
            instance.__invariants__.must_be_satisfied()

        with pytest.raises(CriteriaNotSatisfied):
            cls.__invariants__.must_be_satisfied_by(instance)
