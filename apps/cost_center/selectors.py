from django.db.models.query import QuerySet

from apps.product.filters import ProductFilter
from apps.product.models import Product


def product_list(*, filters=None) -> QuerySet[Product]:
    filters = filters or {}

    qs = Product.objects.all()

    return ProductFilter(filters, qs).qs
