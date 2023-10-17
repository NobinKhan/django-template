from django.contrib import admin

from apps.cost_center.models import CostCenter


@admin.register(CostCenter)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
