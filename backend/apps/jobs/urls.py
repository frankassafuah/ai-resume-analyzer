from rest_framework.routers import DefaultRouter

from apps.jobs.views import JobDescriptionViewSet

app_name = "jobs"

router = DefaultRouter()
# Mounted under /api/v1/jobs/ by config.api_v1, so use an empty prefix here.
router.register(r"", JobDescriptionViewSet, basename="job")

urlpatterns = router.urls
