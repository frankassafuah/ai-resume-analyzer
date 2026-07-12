from django.urls import path

from apps.accounts.views import (
    LoginView,
    LogoutView,
    PasswordForgotView,
    PasswordResetView,
    ProfileView,
    RefreshView,
    RegisterView,
)

app_name = "accounts"

urlpatterns = [
    # Auth
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshView.as_view(), name="refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/password/forgot/", PasswordForgotView.as_view(), name="password-forgot"),
    path("auth/password/reset/", PasswordResetView.as_view(), name="password-reset"),
    # Profile
    path("profile/", ProfileView.as_view(), name="profile"),
]
