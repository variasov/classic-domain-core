from .entities import Value, Entity, Root
from .errors import CriteriaNotSatisfied

from .criteria import Criteria, And, Or, Xor, Invert
from .predicate_wrapping import Predicate, PredicateCriteria, criteria
from .invariants import invariant, is_invariant, HaveInvariants
from .checks import check_arg, check_result

from .repos import (
    Repo, InMemoryRepo, ShelveRepo,
    translate_for, is_translator,
)
