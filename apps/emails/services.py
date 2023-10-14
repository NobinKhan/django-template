from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.emails.models import Email, Role


def create_email(*, email: str = None, role=None) -> Email:
    if not email:
        raise ValidationError(_('Empty Data Not Allowed'))
    email_obj = Email.objects.create(email=email, role=role)
    email_obj.full_clean()
    email_obj.save()
    return email_obj


def create_role(*, name: str = None, description=None) -> Role:
    if not name:
        raise ValidationError(_('Empty Data Not Allowed'))
    role = Role.objects.create(name=name, description=description)
    role.full_clean()
    role.save()
    return role


