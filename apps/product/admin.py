from typing import Any
from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from apps.product.services import create_product_admin
from apps.product.models import Product, SubNumber, Asset, UploadProduct, Tag


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "asset", "sub_number", "inventory_number", "cost_center", "created_by")

    def save_model(self, request: Any, obj, form: Any, change: Any) -> None:
        if change:
            return super().save_model(request, obj, form, change)

        try:
            create_product_admin(**form.cleaned_data)
        except ValidationError as exc:
            self.message_user(request, str(exc), messages.ERROR)


@admin.register(UploadProduct)
class UploadProductAdmin(admin.ModelAdmin):
    list_display = ("id", "asset", "sub_number", "inventory_number", "cost_center","created_by","department")
    # readonly_fields = ("asset", "sub_digit", "tag", "tag_type", "cost_center","created_by", "name")


@admin.register(SubNumber,)
class SubNumberAdmin(admin.ModelAdmin):
    list_display = ("id","number", "created_at", "updated_at")


@admin.register(Asset)
class  AssetAdmin(admin.ModelAdmin):
    list_display = ("id","number", "created_at", "updated_at")


@admin.register(Tag)
class  TagAdmin(admin.ModelAdmin):
    list_display = ("id", "tag", "tag_type", "created_at", "updated_at")

