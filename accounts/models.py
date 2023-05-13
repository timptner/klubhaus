from accounts.validators import StudentEmailValidator, PhoneValidator
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The given email address must be set."))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email_validator = StudentEmailValidator()
    phone_validator = PhoneValidator()

    username = None
    email = models.EmailField(_('email address'), unique=True, validators=[email_validator])
    phone = models.CharField(_('mobile number'), max_length=50, validators=[phone_validator], blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email


class Modification(models.Model):
    REQUESTED = 0
    ACCEPTED = 1
    REJECTED = 2
    STATE_CHOICES = [
        (REQUESTED, "Beantragt"),
        (ACCEPTED, "Angenommen"),
        (REJECTED, "Abgelehnt"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.JSONField("Inhalt")
    state = models.PositiveSmallIntegerField("Status", choices=STATE_CHOICES, default=REQUESTED)
    created_at = models.DateTimeField("Erstellt am", auto_now_add=True)

    class Meta:
        verbose_name = "Veränderung"
        verbose_name_plural = "Veränderungen"
