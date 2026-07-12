from django.urls import path

from apps.common.views import HealthView

app_name = "common"

urlpatterns = [
    # Placeholder v1 root; domain apps append their routes as they land.
    path("health/", HealthView.as_view(), name="v1-health"),
]
