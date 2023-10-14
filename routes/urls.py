from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularRedocView, SpectacularSwaggerView, SpectacularAPIView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(), name="swagger-ui-docs"),
    path("redocs/", SpectacularRedocView.as_view(), name="redoc-ui-docs"),
    # path("api/", include(("apps.api.urls", "api"))),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

