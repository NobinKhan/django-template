from django.urls import include, path
from apps.product.apis import (
    DashBoardDeatilsApi
)


urlpatterns = [
    path("auth/", include(("apps.authentication.urls", "authentication"))),
    path("user/", include(("apps.users.urls", "user"))),
    path("product/", include(("apps.product.urls", "product"))),
    path("cost_center/", include(("apps.cost_center.urls", "cost_center"))),
    path("email/", include(("apps.emails.urls", "email"))),
    path("dashboard/",DashBoardDeatilsApi.as_view(),name='dashboard'),
]


