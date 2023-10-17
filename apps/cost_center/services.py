from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.cost_center.models import CostCenter


def create_cost_center(*, name: str = None) -> CostCenter:
    if not name:
        raise ValidationError(_("Empty Data Not Allowed"))

    # object creation
    cost_center = CostCenter.objects.get_or_create(name=name)
    return cost_center
