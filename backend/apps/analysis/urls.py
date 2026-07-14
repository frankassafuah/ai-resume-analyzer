from rest_framework.routers import DefaultRouter

from apps.analysis.views import AnalysisViewSet

app_name = "analysis"

router = DefaultRouter()
router.register(r"", AnalysisViewSet, basename="analysis")

urlpatterns = router.urls
