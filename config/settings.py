import os
import dj_database_url
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-placeholder')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'strings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================
# 🗄️ DATABASES — Local MySQL + Heroku Cloud Auto Switch
# ============================================================

# if DEBUG:
#     # Local MySQL setup
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': config('DB_NAME', default='strings_db'),
#             'USER': config('DB_USER', default='root'),
#             'PASSWORD': config('DB_PASSWORD', default=''),
#             'HOST': config('DB_HOST', default='127.0.0.1'),
#             'PORT': config('DB_PORT', default='3306'),
#         }
#     }
# else:
#     # Production (Heroku)
#     DATABASES = {
#     'default': dj_database_url.config(
#         default=config('DATABASE_URL'),
#         conn_max_age=600,
#         conn_health_checks=True,
#     )
# }

if config('DEBUG', default=True, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQLDATABASE'),
            'USER': os.environ.get('MYSQLUSER'),
            'PASSWORD': os.environ.get('MYSQLPASSWORD'),
            'HOST': os.environ.get('MYSQLHOST'),
            'PORT': os.environ.get('MYSQLPORT'),
        }
    }

# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
