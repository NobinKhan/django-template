from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from settings.configs.env import ENVIRONMENT

urlpatterns = [
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(), name="swagger-ui-docs"),
    path("redocs/", SpectacularRedocView.as_view(), name="redoc-ui-docs"),
    # path("api/", include(("apps.api.urls", "api"))),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# debug toolbar for local and development
if ENVIRONMENT in ("local", "development"):
    urlpatterns.append(path("debug/", include("debug_toolbar.urls")))
