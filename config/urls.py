from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Login: send username and password, receive access and refresh tokens.
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Exchange a refresh token for a new access token.
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # API documentation: the raw schema and the interactive Swagger page.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # All other API endpoints live under /api/.
    path("api/", include("applications.urls")),
]
