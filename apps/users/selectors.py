from django.db.models.query import QuerySet

from apps.users.filters import UserFilter
from apps.users.models import User


def user_get_login_data(*, user: User):
    return {
        "id": user.id,
        "username": user.username,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    }


def user_list(*, filters=None) -> QuerySet[User]:
    filters = filters or {}

    qs = User.objects.all().order_by("-id").exclude(is_superuser=True, is_staff=True)

    return UserFilter(filters, qs).qs
