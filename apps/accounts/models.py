"""User accounts, roles and auth-support models."""
import secrets
import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

from apps.core.models import District, Region


class UserManager(BaseUserManager):
    """Manager for the email-based custom user model."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", User.Role.SUPER_ADMIN)
        extra.setdefault("is_verified", True)
        if extra.get("is_staff") is not True or extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_staff and is_superuser set to True")
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    """Custom user keyed by email with a platform role."""

    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        BUSINESS_OWNER = "business_owner", "Business Owner"
        BUYER = "buyer", "Buyer"
        SELLER = "seller", "Seller"
        JOB_SEEKER = "job_seeker", "Job Seeker"

    # Remove the username field; authenticate with email.
    username = None
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    email = models.EmailField("email address", unique=True, db_index=True)
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.BUYER, db_index=True
    )
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL)
    district = models.ForeignKey(District, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ("-date_joined",)
        indexes = [models.Index(fields=["role", "is_verified"])]

    def __str__(self):
        return self.email

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser

    @property
    def full_name(self):
        return self.get_full_name() or self.email


class JobSeekerProfile(models.Model):
    """Extended profile for job seekers (CV, headline, experience)."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="job_seeker_profile"
    )
    headline = models.CharField(max_length=160, blank=True)
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=400, blank=True, help_text="Comma-separated skills")
    years_experience = models.PositiveSmallIntegerField(default=0)
    cv = models.FileField(upload_to="cvs/", blank=True, null=True)
    open_to_work = models.BooleanField(default=True)

    def __str__(self):
        return f"JobSeekerProfile<{self.user.email}>"


class _BaseToken(models.Model):
    """Abstract one-time token with expiry."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    ttl = timedelta(hours=24)

    @classmethod
    def issue(cls, user):
        return cls.objects.create(user=user, token=secrets.token_urlsafe(32))

    @property
    def is_valid(self):
        return self.used_at is None and timezone.now() <= self.created_at + self.ttl

    def consume(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])


class EmailVerificationToken(_BaseToken):
    ttl = timedelta(days=3)


class PasswordResetToken(_BaseToken):
    ttl = timedelta(hours=2)
