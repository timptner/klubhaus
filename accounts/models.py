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
    email = models.EmailField("E-Mail-Adresse", unique=True, validators=[email_validator])
    phone = models.CharField("Mobilnummer", max_length=50, validators=[phone_validator], blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = "Benutzer"
        verbose_name_plural = "Benutzer"
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
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.user.get_full_name()

    def get_state_color(self) -> str:
        colors = {
            self.REQUESTED: 'is-light',
            self.ACCEPTED: 'is-light is-success',
            self.REJECTED: 'is-light is-danger',
        }
        return colors[self.state]

    def content_with_labels(self) -> dict:
        labels = {}
        for field, value in self.content.items():
            label = User._meta.get_field(field).verbose_name
            labels[label] = value
        return labels
