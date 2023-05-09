import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class StudentEmailValidator(validators.RegexValidator):
    regex = r'^[\w-.]+@st\.ovgu\.de$'
    message = _(
        "Enter a valid email address. This value may contain only English letters, "
        "numbers, and dot characters. The email address must end with '@st.ovgu.de'."
    )
    flags = re.ASCII


@deconstructible
class PhoneValidator(validators.RegexValidator):
    regex = r'^\+[\d]+$'
    message = _(
        "Enter a valid mobile number. This value may contain only numbers. Make "
        "sure to assign a country code with a plus sign at the beginning."
    )
    flags = re.ASCII
