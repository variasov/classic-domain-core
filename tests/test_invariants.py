from dataclasses import field

import pytest

from classic.domain import entity, value_obj, root, invariant


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
    (SomeEntity(1, 123, 'value'), True),
    (SomeRoot(1, 123, 'value', child=[
        SomeEntity(1, 123, 'value'),
        SomeEntity(2, 123, 'value'),
    ]), True),
))
def test_invariants_on_value(instance, value):
    assert instance.all_invariants(instance) is value
