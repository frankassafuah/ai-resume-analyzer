from apps.accounts.models import User
from apps.common.filters import BaseFilterSet


class UserFilter(BaseFilterSet):
    class Meta:
        model = User
        fields = ["is_active", "email_verified"]
