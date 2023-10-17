from uuid import uuid4

from apps.common.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.


class AccessToken(BaseModel):
    # Choices With enum functionality
    class TokenValidity(models.TextChoices):
        VALID = "valid", _("Valid")
        INVALID = "invalid", _("Invalid")

    def _generate_token():
        return uuid4().hex

    def _expire_time():
        return timezone.now() + timezone.timedelta(days=7)

    user = models.ForeignKey(
        get_user_model(),
        related_name="tokens",
        on_delete=models.CASCADE,
        editable=False,
        null=True,
        blank=True,
    )
    token = models.UUIDField(
        default=_generate_token, editable=False, null=True, blank=True
    )
    exp = models.DateTimeField(default=_expire_time, editable=False)
    validity = models.CharField(
        default=TokenValidity.VALID,
        choices=TokenValidity.choices,
        max_length=10,
        blank=True,
        null=True,
    )
