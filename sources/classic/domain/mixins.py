import inspect

from .criteria import Criteria
from .errors import CriteriaNotMet


class CriteriaMixin:

    def are(self, criteria_: Criteria):
        return criteria_.is_satisfied_by(self)

    def must_satisfy(self, criteria_: Criteria):
        if not criteria_.is_satisfied_by(self):
            raise CriteriaNotMet(criteria_, self)


class CheckMixin:

    def __init_subclass__(cls, **kwargs):
        cls.checks = [
            method
            for name, method in inspect.getmembers(cls)
            if callable(method) and name.startswith('check_')
        ]

    def check(self, quick: bool = False):
        failed = []
        for check in self.checks:
            result = check()
            if result:
                if quick:
                    raise result
                failed.append(result)
        if failed:
            raise ErrorsList[failed]
