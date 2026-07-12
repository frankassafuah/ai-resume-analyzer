from apps.accounts.models import User
from apps.common.repositories import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self.get_or_none(email=email.strip().lower())
