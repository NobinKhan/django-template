from django.urls import include, path

from apps.users.apis import (
    Me,
    RoleList,
    SelfDelete,
    UpdateUser,
    UserDeleteView,
    UserListApi,
)

urlpatterns = [
    path("list/", UserListApi.as_view(), name="user_list"),
    path("change/<int:pk>/", UpdateUser.as_view(), name="change_user"),
    path("UserDelete/<int:pk>/", UserDeleteView.as_view(), name="UserDelete"),
    path("<int:pk>/delete/", SelfDelete.as_view(), name="user_delete"),
    path("me/", Me.as_view(), name="me"),
    path(
        "role/",
        include(
            (
                [
                    path("list/", RoleList.as_view(), name="role_list"),
                ],
                "role",
            )
        ),
    ),
]
