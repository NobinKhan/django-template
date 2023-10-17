from django.urls import include, path

from apps.cost_center.apis import CostCenterListApi, CreateCostCenter

urlpatterns = [
    path(
        "",
        include(
            (
                [
                    path(
                        "create/", CreateCostCenter.as_view(), name="create_cost_center"
                    ),
                    path("list/", CostCenterListApi.as_view(), name="list_cost_center"),
                ],
                "cost_center",
            )
        ),
    ),
]
