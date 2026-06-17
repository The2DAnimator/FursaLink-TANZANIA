from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import (
    EmailVerificationToken,
    JobSeekerProfile,
    PasswordResetToken,
)
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    JobSeekerProfileSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    RoleTokenObtainPairSerializer,
    UserSerializer,
)
from apps.accounts.tasks import send_password_reset_email, send_verification_email
from apps.core.permissions import IsAdmin

User = get_user_model()


class RoleTokenObtainPairView(TokenObtainPairView):
    serializer_class = RoleTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_scope = "otp"
    throttle_classes = [ScopedRateThrottle]

    def perform_create(self, serializer):
        user = serializer.save()
        token = EmailVerificationToken.issue(user)
        send_verification_email.delay(user.id, token.token)


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses={200: None})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            evt = EmailVerificationToken.objects.select_related("user").get(
                token=serializer.validated_data["token"]
            )
        except EmailVerificationToken.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        if not evt.is_valid:
            return Response({"detail": "Token expired or used."}, status=status.HTTP_400_BAD_REQUEST)
        evt.user.is_verified = True
        evt.user.save(update_fields=["is_verified"])
        evt.consume()
        return Response({"detail": "Email verified."})


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    throttle_scope = "otp"
    throttle_classes = [ScopedRateThrottle]

    @extend_schema(responses={200: None})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Always return 200 to avoid leaking which emails exist.
        user = User.objects.filter(email__iexact=serializer.validated_data["email"]).first()
        if user:
            token = PasswordResetToken.issue(user)
            send_password_reset_email.delay(user.id, token.token)
        return Response({"detail": "If the account exists, a reset link has been sent."})


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses={200: None})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            prt = PasswordResetToken.objects.select_related("user").get(
                token=serializer.validated_data["token"]
            )
        except PasswordResetToken.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        if not prt.is_valid:
            return Response({"detail": "Token expired or used."}, status=status.HTTP_400_BAD_REQUEST)
        prt.user.set_password(serializer.validated_data["new_password"])
        prt.user.save(update_fields=["password"])
        prt.consume()
        return Response({"detail": "Password updated."})


class MeViewSet(viewsets.ViewSet):
    """Operations on the currently authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def list(self, request):
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["patch"])
    def update_profile(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password changed."})

    @action(detail=False, methods=["get", "put", "patch"], url_path="job-seeker-profile")
    def job_seeker_profile(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
        if request.method == "GET":
            return Response(JobSeekerProfileSerializer(profile).data)
        serializer = JobSeekerProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserAdminViewSet(viewsets.ModelViewSet):
    """Super-admin user management."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ("role", "is_verified", "is_active")
    search_fields = ("email", "first_name", "last_name", "phone")

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        user = self.get_object()
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(UserSerializer(user).data)
