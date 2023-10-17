from apps.common.models import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class CostCenter(BaseModel):
    name = models.CharField(
        verbose_name=_("Cost-Center"), max_length=15, unique=True, null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                ],
                name="unique_cost_center",
            )
        ]

    def __str__(self):
        return f"{self.name}"
