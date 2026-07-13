from rest_framework.routers import DefaultRouter

from apps.resumes.views import ResumeViewSet

app_name = "resumes"

router = DefaultRouter()
# Mounted under /api/v1/resumes/ by config.api_v1, so use an empty prefix here.
router.register(r"", ResumeViewSet, basename="resume")

urlpatterns = router.urls
