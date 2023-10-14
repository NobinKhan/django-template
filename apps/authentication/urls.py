from django.urls import include, path

from apps.authentication.apis import (
    Login,
    Register,
    Logout,
    Refresh,
)

urlpatterns = [
    path("",include(([
        path("login/", Login.as_view(), name="login"),
        path("register/", Register.as_view(), name="register"),
        path("logout/", Logout.as_view(), name="logout"),
        path("refresh/", Refresh.as_view(), name="refresh"),
    ],"session",)),),

    # path("jwt/",include(([
    #     path("login/", UserJwtLoginApi.as_view(), name="login"),
    #     path("logout/", UserJwtLogoutApi.as_view(), name="logout"),
    # ],"jwt",)),),
    # path("me/", UserMeApi.as_view(), name="me"),
]
