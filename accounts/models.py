import re

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
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
    email_validator = RegexValidator(
        regex=r'^[^\s]+@(st\.ovgu\.de|stud\.h2\.de)$',
        message=("Die E-Mail-Adresse darf nur aus Buchstaben, Ziffern, Bindestrichen oder Punkten bestehen und muss "
                 "mit \"@st.ovgu.de\" oder \"@stud.h2.de\" enden."),
        flags=re.ASCII,
    )
    phone_validator = RegexValidator(
        regex=r'^\+[\d]+$',
        message=("Die Mobilnummer darf nur aus Ziffern bestehen und muss einen Ländercode, beginnen mit einem "
                 "Pluszeichen, besitzen."),
        flags=re.ASCII,
    )
    student_validator = RegexValidator(
        regex=r'^\d{6}$',
        message="Die Matrikelnummer darf nur aus sechs Ziffern bestehen.",
        flags=re.ASCII,
    )

    MECHANICS = 'FMB'
    PROCESSING = 'FVST'
    ELECTRICS = 'FEIT'
    COMPUTER = 'FIN'
    MATHEMATICS = 'FMA'
    NATURE = 'FNW'
    MEDICINE = 'FME'
    HUMANITIES = 'FHW'
    ECONOMICS = 'FWW'

    FACULTY_CHOICES = [
        (MECHANICS,  "Maschinenbau"),
        (PROCESSING, "Verfahrens- und Systemtechnik"),
        (ELECTRICS, "Elektro- und Informationstechnik"),
        (COMPUTER, "Informatik"),
        (MATHEMATICS, "Mathematik"),
        (NATURE, "Naturwissenschaften"),
        (MEDICINE, "Medizin"),
        (HUMANITIES, "Humanwissenschaften"),
        (ECONOMICS, "Wirtschaftswissenschaften"),
    ]

    username = None
    email = models.EmailField("E-Mail-Adresse", unique=True, validators=[email_validator])
    phone = models.CharField("Mobilnummer", max_length=50, validators=[phone_validator], blank=True)
    student = models.CharField("Matrikelnummer", max_length=6, unique=True,
                               validators=[student_validator], blank=True, null=True)
    faculty = models.CharField("Fakultät", max_length=4, choices=FACULTY_CHOICES, blank=True)

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
