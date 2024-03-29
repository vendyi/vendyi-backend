"""
Django settings for Vendyi Backend Development mode project.
"""
from pathlib import Path
import dj_database_url
import os
from dotenv import load_dotenv
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-^wbhrscow-t%)$i91i#oy-b4&rm4g)7$3v41ur2h1=+wmq)l+i"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    # Include any other authentication backends you are using
]
REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'dj_rest_auth.serializers.LoginSerializer',
    'TOKEN_SERIALIZER': 'dj_rest_auth.serializers.TokenSerializer',
    'USER_DETAILS_SERIALIZER': 'accounts.serializers.FullUserSerializer',
}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',  # Include TokenAuthentication
        # ... other authentication classes
    ),
    # ... other DRF settings
}


# Application definition
INSTALLED_APPS = [
    'daphne',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django_filters',
    'django_cryptography',
    "accounts",
    "bonus",
    "cart",
    "delivery",
    "payment",
    "product",
    "vendors",
    'rest_framework',
    'rest_framework.authtoken',
    'channels',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'chat',
    'dj_rest_auth',
    'storages',
]
SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ...
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DATABASES['default'] = dj_database_url.parse(os.environ.get('DATABASE_URL'))


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

CSRF_TRUSTED_ORIGINS = ['https://vendyi-92322aa588dc.herokuapp.com','https://192.168.43.142:8081']

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Assuming you have set these environment variables correctly
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")

# If you are using DigitalOcean Spaces, this endpoint URL is needed
AWS_S3_ENDPOINT_URL = "https://ams3.digitaloceanspaces.com"

# This is for cache settings, it looks fine
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

# This should be just the path prefix within the bucket, not the full URL
AWS_LOCATION = 'media'

# Your static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

# WhiteNoise settings look fine, assuming you have 'whitenoise' installed
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# For media files with S3 storage
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.ams3.digitaloceanspaces.com/{AWS_LOCATION}/"
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# MEDIA_ROOT is not typically used when DEFAULT_FILE_STORAGE is set to S3, but it is still required for certain Django functions
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = 'accounts.User'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.environ.get('REDIS_URL'), 12340)],
        },
    },
}

ASGI_APPLICATION = 'core.asgi.application'
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# settings.py

EXPRESSPAY_API_KEY = os.environ.get('EXPRESSPAY_API_KEY')
EXPRESSPAY_MERCHANT_ID = os.environ.get('EXPRESSPAY_MERCHANT_ID')
# ... other configuration as needed
# settings.py
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
CORS_ALLOW_ALL_ORIGINS = True