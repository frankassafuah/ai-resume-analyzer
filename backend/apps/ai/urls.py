from rest_framework.routers import DefaultRouter

app_name = "ai"

router = DefaultRouter()
# router.register(...)   # added with this app's endpoints

urlpatterns = router.urls
