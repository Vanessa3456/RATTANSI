from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
import re


# Function to validate registration number format
def validate_reg_number(value):
    pattern = r'^[A-Z]{3}/[A-Z]/01-\d{5}/\d{4}$'
    if not re.match(pattern, value):
        raise ValidationError(
            "Registration number must be in the format: ABC/X/01-XXXXX/YYYY (e.g., SIT/B/01-00001/2000)."
        )


# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, full_name=None, password=None, reg_number=None, is_staff=False, is_superuser=False):
        """Creates a user - Applicants use reg_number, staff/admins use email."""

        if is_staff or is_superuser:
            if not email:
                raise ValueError("Staff and Superusers must have an email address.")

        if not is_staff and not is_superuser and not reg_number:
            raise ValueError("Applicants must have a registration number.")

        email = self.normalize_email(email) if email else None

        user = self.model(
            email=email,
            full_name=full_name,
            reg_number=reg_number,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=True if is_staff or is_superuser else False,  # Superusers and staff are active immediately
            is_applicant=not is_staff and not is_superuser  # Only applicants get `is_applicant=True`
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password):
        """Creates a superuser (Admin) who logs in using email."""
        return self.create_user(
            email=email,
            full_name=full_name,
            password=password,
            is_staff=True,
            is_superuser=True
        )


# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    reg_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        validators=[validate_reg_number],
        verbose_name="Registration Number"
    )
    email = models.EmailField(
        max_length=191,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Email Address"
    )
    full_name = models.CharField(max_length=100, verbose_name="Full Name")
    is_active = models.BooleanField(default=False)  # Default inactive for applicants
    is_staff = models.BooleanField(default=False)  # Staff/Admins
    is_superuser = models.BooleanField(default=False)  # Superusers
    is_applicant = models.BooleanField(default=True)  # Default to applicant
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  #  Superusers & staff log in using email
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.email if self.is_staff or self.is_superuser else self.reg_number})"
