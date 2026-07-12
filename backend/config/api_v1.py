"""API v1 URL aggregator.

Each domain app owns a `urls.py` exposing a DRF router; they are mounted under a
stable prefix here. The whole module is included under `/api/v1/` with the
namespace "v1" (see config/urls.py), which drives DRF's NamespaceVersioning.
"""
from django.urls import include, path

app_name = "v1"

urlpatterns = [
    path("accounts/", include("apps.accounts.urls")),
    path("resumes/", include("apps.resumes.urls")),
    path("jobs/", include("apps.jobs.urls")),
    path("analysis/", include("apps.analysis.urls")),
    path("ai/", include("apps.ai.urls")),
    path("notifications/", include("apps.notifications.urls")),
]
