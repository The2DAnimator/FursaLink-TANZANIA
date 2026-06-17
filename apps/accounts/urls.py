from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apps.accounts.views import (
    MeViewSet,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    RoleTokenObtainPairView,
    UserAdminViewSet,
    VerifyEmailView,
)

router = DefaultRouter()
router.register("admin/users", UserAdminViewSet, basename="admin-users")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", RoleTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/verify-token/", TokenVerifyView.as_view(), name="token_verify"),
    path("auth/verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("auth/password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path(
        "auth/password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("me/", MeViewSet.as_view({"get": "list"}), name="me"),
    path(
        "me/update-profile/",
        MeViewSet.as_view({"patch": "update_profile"}),
        name="me-update-profile",
    ),
    path(
        "me/change-password/",
        MeViewSet.as_view({"post": "change_password"}),
        name="me-change-password",
    ),
    path(
        "me/job-seeker-profile/",
        MeViewSet.as_view(
            {"get": "job_seeker_profile", "put": "job_seeker_profile", "patch": "job_seeker_profile"}
        ),
        name="me-job-seeker-profile",
    ),
] + router.urls
