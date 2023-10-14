import django_filters

from apps.product.models import Product


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = ("id", "asset_id", "timestamp", "created_by")
