from .criteria import Criteria


class CriteriaNotMet(Exception):
    """
    Исключение, свидетельствующее о неудовлетворении критерия
    """

    def __init__(self, criteria: Criteria):
        self.criteria = criteria


class CheckFailed(Exception):
    """
    Исключение, возникающее при проваленной проверке
    """

    def __init__(self, check: str):
        self.check = check
