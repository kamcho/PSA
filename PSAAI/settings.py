"""
Django settings for PSAAI project.

Generated by 'django-admin startproject' using Django 4.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
import Logs

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*1r4hwdyal=y_j%*m&+-_4!@j)33!9a(z*k_%71c($@&71fbue'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1','*','http://crimsons-analytics.com/','crimsons-analytics.com']
CSRF_TRUSTED_ORIGINS = ["http://16.170.243.46","https://107a-154-123-60-86.ngrok-free.app"]

# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'Users',
    'SubjectList',
    'Exams',
    'Guardian',
    'Analytics',
    'Teacher',
    'Supervisor',
    'Logs',
    'Subscription',
    'crispy_bootstrap4',
    'Support',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'PSAAI.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'PSAAI.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql_psycopg2',
       'NAME': 'psaai',
       'USER': 'root',
       'PASSWORD': '141778215aA',
       'HOST': 'psaai.covjv7kf4u4o.eu-north-1.rds.amazonaws.com',
       'PORT': '5432',
   }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'psaai',         # The name of your PostgreSQL database
#         'USER': 'postgres',     # The PostgreSQL superuser
#         'PASSWORD': '141778215aA',  # The password you set during PostgreSQL installation
#         'HOST': 'localhost',    # The database server (in this case, it's your local machine)
#         'PORT': '5432',             # Leave empty to use the default PostgreSQL port (5432)
#     }
# }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'custom_handler': {
            'level': 'DEBUG',
            'class': 'Logs.logging.DatabaseLogHandler',  # Correct Python path
        },
        'mail_admins': {
            'level': 'INFO',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        },
    },
    'loggers': {
        'django': {
            'handlers': ['custom_handler'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
ADMINS = [('Kevin', 'njokevin9@gmail.com')]
SERVER_EMAIL = 'njokevin9@gmail.com'

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/


STATIC_URL = 'static/'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# PERSONAL CONFIGS
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
AUTH_USER_MODEL = 'Users.MyUser'
LOGIN_REDIRECT_URL = 'redirect'
# CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = 'bootstrap4'
LOGIN_URL = 'Sign-In/'




# VARIABLES

email = os.environ.get('SchoolMail')
password = os.environ.get('SchoolMaidPassword')
service_api = os.environ.get('MailServiceAPI')
service_id = os.environ.get('ServiceID')
school_id = os.environ.get('SchoolID')


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "njokevin999@gmail.com"
EMAIL_HOST_PASSWORD = "zjlnawmazkfsehid"
service = '53B9834AAB562891E2D041ECF0A05A64FE33'
APIKEY = '3699E6F03C0DBDF11D23F7E4582F51753069D25F9E0FCCE778A66472288716D0C15FFD467AB83F885BE10DB6CDDA6C49'
SCHOOL_ID = '3d627dc5-da9f-4582-9a9c-31ce81448784'
ASGI_APPLICATION = "PSAAI.asgi.application"

