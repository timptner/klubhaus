import django

from dj_database_url import parse as db_url
from django.contrib.messages import constants as message_constants
# noinspection PyPackageRequirements
from decouple import config, Csv, Choices
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'accounts',
    'excursions',
    'home',
    'merchandise',
    'tournament',
    'volunteers',

    'fontawesomefree',

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

ROOT_URLCONF = 'klubhaus.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'klubhaus/templates',
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

WSGI_APPLICATION = 'klubhaus.wsgi.application'


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

LOGIN_REDIRECT_URL = 'accounts:profile'


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'klubhaus' / 'static',
]

STATIC_ROOT = config('STATIC_ROOT', default=str(BASE_DIR / 'static'))


# Media files

MEDIA_URL = 'media/'

MEDIA_ROOT = config('MEDIA_ROOT', default=str(BASE_DIR / 'media'))


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Forms

FORM_RENDERER = 'klubhaus.forms.BulmaFormRenderer'


# Messages

MESSAGE_TAGS = {
    message_constants.DEBUG: '',
    message_constants.INFO: 'is-info',
    message_constants.SUCCESS: 'is-success',
    message_constants.WARNING: 'is-warning',
    message_constants.ERROR: 'is-danger',
}


# Email

EMAIL_BACKEND = 'klubhaus.mails.EmailBackend'

DEFAULT_FROM_EMAIL = config('MAIL_SENDER', default='"Klubhaus" <klubhaus@farafmb.de>')

SERVER_EMAIL = config('MAIL_ADMIN', default='server@farafmb.de')

POSTMARK_API_TOKEN = config('POSTMARK_API_TOKEN', default=None)


# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {
            'format': '[%(asctime)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(name)s %(message)s',
        },
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'console2': {
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': config('LOG_FILE', default=BASE_DIR / 'klubhaus.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': config('LOG_HANDLERS', default='console', cast=Csv()),
        'level': config('LOG_LEVEL', default='WARNING',
                        cast=Choices(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])),
    },
    'loggers': {
        'django': {
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['console2'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'PIL': {
            'level': 'WARNING',
        },
    },
}
