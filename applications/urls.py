from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import JobApplicationViewSet

# The router generates the list, detail, create, update and delete
# URLs for the viewset automatically.
router = DefaultRouter()
router.register("applications", JobApplicationViewSet, basename="application")

urlpatterns = [
    path("", include(router.urls)),
]