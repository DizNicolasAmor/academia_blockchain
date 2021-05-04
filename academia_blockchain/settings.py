"""
Django settings for academia_blockchain project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import ast
import os
import django_heroku
import dj_database_url
import logging

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/
def get_env_variable(variable_name):
    try:
        v = os.environ[variable_name]
    except Exception as e:
        v = "na"
    return v

ALLOWED_HOSTS = ["*"]
DEBUG = True
DOCKER = get_env_variable('ENV') == "local" and get_env_variable('DOCKER') == "True"
HEROKU = get_env_variable('ENV') == "HEROKU"
SECRET_KEY = get_env_variable('ACADEMIA_BLOCKCHAIN_SKEY')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'profiles',
    'courses',
    'star_ratings',
    'taggit'
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

CSRF_COOKIE_NAME = 'csrftoken'

ROOT_URLCONF = 'academia_blockchain.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export'
            ],
        },
    },
]

SETTINGS_EXPORT = [
  'CSRF_COOKIE_NAME'
]

WSGI_APPLICATION = 'academia_blockchain.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

if HEROKU:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

if DOCKER:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR + "/media/"
STATIC_ROOT = 'staticfiles/'
STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

if HEROKU:
    AWS_ACCESS_KEY_ID = get_env_variable('AWSAccessKeyId')
    AWS_SECRET_ACCESS_KEY = get_env_variable('AWSSecretKey')
    AWS_STORAGE_BUCKET_NAME = get_env_variable('AWS_STORAGE_BUCKET_NAME')
    S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
    STATIC_URL = S3_URL
    MEDIA_URL = S3_URL
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_DEFAULT_ACL = None

    # Email
    MAILGUN_API_KEY = get_env_variable('MAILGUN_API_KEY')
    MAILGUN_DOMAIN = get_env_variable('MAILGUN_DOMAIN')
    MAILGUN_PUBLIC_KEY = get_env_variable('MAILGUN_PUBLIC_KEY')
    MAILGUN_SMTP_LOGIN = get_env_variable('MAILGUN_SMTP_LOGIN')
    MAILGUN_SMTP_PASSWORD = get_env_variable('MAILGUN_SMTP_PASSWORD')
    MAILGUN_SMTP_PORT = get_env_variable('MAILGUN_SMTP_PORT')
    MAILGUN_SMTP_SERVER = get_env_variable('MAILGUN_SMTP_SERVER')

# Logging
LOGGING = {
    "version": 1,
    "loggers": {"app_logger": {"level": "DEBUG", "handlers": ["console"]}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "verbose"}},
    "formatters": {"verbose": {"format": "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"}}
}


# Other config
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "event_index"
LOGOUT_REDIRECT_URL = "event_index"
LANGUAGE_CODE = "es-ES"

if HEROKU:
    django_heroku.settings(locals())
