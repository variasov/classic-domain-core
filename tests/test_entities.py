from dataclasses import dataclass, field

import pytest

from classic.domain.core import (
    Value, Entity, Root,
    invariant, CriteriaNotSatisfied,
)


@dataclass
class Base:
    int_field: int
    str_field: str

    @invariant
    def check_int_field(self):
        return isinstance(self.int_field, int)

    @invariant
    def check_str_field(self):
        return isinstance(self.str_field, str)


class SomeValue(Base, Value):
    pass


class SomeEntity(Base, Entity):
    pass


class SomeRoot(Base, Root):
    child: list[SomeEntity] = field(default_factory=list)


@pytest.mark.parametrize('instance,value', (
    (SomeValue(123, 'value'), True),
    (SomeValue(None, 'value'), False),
    (SomeValue(123, None), False),
    (SomeValue(None, None), False),
    (SomeEntity(1, 123, 'value'), True),
    (SomeRoot(1, 123, 'value', child=[
        SomeEntity(1, 123, 'value'),
        SomeEntity(1, 123, 'value'),
    ]), True),
))
def test_invariants_on_value(instance, value):
    cls = instance.__class__

    assert cls.invariants.is_satisfied_by(instance) is value
    assert instance.invariants() is value
    assert instance.invariants.is_satisfied() is value

    if not value:
        with pytest.raises(CriteriaNotSatisfied):
            instance.invariants.must_be_satisfied()

        with pytest.raises(CriteriaNotSatisfied):
            cls.invariants.must_be_satisfied_by(instance)
