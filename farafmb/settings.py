import django

from dj_database_url import parse as db_url
from django.contrib.messages import constants as message_constants
# noinspection PyPackageRequirements
from decouple import config, Csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'accounts',
    'home',

    'anymail',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'farafmb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'farafmb/templates',
            django.__path__[0] + '/forms/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'farafmb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': config('DATABASE_URL', default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'), cast=db_url)
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Authentication

AUTH_USER_MODEL = 'accounts.User'


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Forms

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'


# Messages

MESSAGE_TAGS = {
    message_constants.DEBUG: '',
    message_constants.INFO: 'is-info',
    message_constants.SUCCESS: 'is-success',
    message_constants.WARNING: 'is-warning',
    message_constants.ERROR: 'is-danger',
}


# Email

ANYMAIL = {
    'POSTMARK_SERVER_TOKEN': config('POSTMARK_API_TOKEN'),
    'SEND_DEFAULTS': {
        'esp_extra': {'MessageStream': 'farafmb-party'},
    }
}

EMAIL_BACKEND = 'anymail.backends.postmark.EmailBackend'

DEFAULT_FROM_EMAIL = '"[Party] Fachschaftsrat Maschinenbau" <party@farafmb.de>'

SERVER_EMAIL = '"[Server] Fachschaftsrat Maschinenbau" <server@farafmb.de>'
