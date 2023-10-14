from django.contrib import admin

from apps.cost_center.models import CostCenter
from apps.cost_center.services import create_cost_center



@admin.register(CostCenter)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", 'name',)
    


