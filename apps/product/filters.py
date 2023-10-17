import django_filters

from apps.product.models import Product, UploadProduct


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = (
            "id",
            "asset",
            "sub_digit",
            "cost_center",
            "created_by",
            "email_sent_status",
            "send_by",
        )


class UploadProductFilter(django_filters.FilterSet):
    class Meta:
        model = UploadProduct
        fields = ("id", "asset", "sub_digit", "cost_center", "created_by")
