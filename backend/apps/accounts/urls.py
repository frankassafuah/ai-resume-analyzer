from rest_framework.routers import DefaultRouter

app_name = "accounts"

router = DefaultRouter()
# router.register("users", UserViewSet, basename="user")   # M1

urlpatterns = router.urls
