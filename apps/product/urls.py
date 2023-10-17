from django.urls import include, path

from apps.product.apis import (
    CreateSubNumber,
    CreateUploadProduct,
    DeleteProduct,
    DeleteScannedProduct,
    GetScannedProduct,
    ProductList,
    ScanProduct,
    UploadProductList,
)

urlpatterns = [
    path(
        "",
        include(
            (
                [
                    path("scan/", ScanProduct.as_view(), name="scan_product"),
                    path("list/", ProductList.as_view(), name="list_product"),
                    path(
                        "create/", CreateUploadProduct.as_view(), name="create_product"
                    ),
                    path(
                        "ns_list/", UploadProductList.as_view(), name="list_ns_product"
                    ),
                    path(
                        "scanned/", GetScannedProduct.as_view(), name="scanned_products"
                    ),
                    path(
                        "delete/", DeleteProduct.as_view(), name="delete_product_list"
                    ),
                    path(
                        "delete/<int:pk>/",
                        DeleteProduct.as_view(),
                        name="delete_single_product",
                    ),
                    path(
                        "delete_sp/",
                        DeleteScannedProduct.as_view(),
                        name="delete_scanned_products",
                    ),
                    path(
                        "delete_sp/<int:pk>/",
                        DeleteScannedProduct.as_view(),
                        name="delete_scanned_product_id",
                    ),
                ],
                "product",
            )
        ),
    ),
    path(
        "sub_number/",
        include(
            (
                [
                    path(
                        "create/", CreateSubNumber.as_view(), name="create_sub_number"
                    ),
                ],
                "sub_number",
            )
        ),
    ),
]
