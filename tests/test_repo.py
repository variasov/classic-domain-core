import pytest

from classic.domain.core import Repo, Root, InMemoryRepo, criteria


class SomeEntity(Root):
    id: int
    value: str

    @criteria
    def value_greater_than(self, other):
        return self.value > other


@pytest.fixture
def in_memory_repo():
    return InMemoryRepo[SomeEntity]()


class TestRepo:

    @pytest.fixture
    def repo(self):
        raise NotImplemented

    def test_save(self, repo: Repo):
        instance = SomeEntity(1, '1')
        repo.save(instance)

        instance_from_repo = repo.get(1)

        assert instance == instance_from_repo
