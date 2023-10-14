from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.token.models import AccessToken
from apps.users.models import User

def create_token(user: User):
    if not user.is_active:
        raise ValidationError(_("User is not active"))
    
    token = AccessToken(user=user)
    token.save()
    return token.token