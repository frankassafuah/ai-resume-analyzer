"""Account services. Auth flows (register/login/verify/OAuth) land in M1;
this establishes the service + repository wiring."""
from apps.accounts.repositories import UserRepository
from apps.common.services import BaseService


class AccountService(BaseService):
    def __init__(self, users: UserRepository | None = None) -> None:
        super().__init__()
        self.users = users or UserRepository()
