from django.db.models.query import QuerySet

from apps.product.filters import ProductFilter, UploadProductFilter
from apps.product.models import Product, UploadProduct



def product_list(*, filters=None) -> QuerySet[Product]:
    filters = filters or {}

    qs = Product.objects.all().order_by('-id')

    return ProductFilter(filters, qs).qs


def upload_product_list(*, filters=None) -> QuerySet[UploadProduct]:
    filters = filters or {}

    qs = UploadProduct.objects.all()

    return UploadProductFilter(filters, qs).qs
