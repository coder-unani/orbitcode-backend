import logging
import os
from datetime import datetime
from pathlib import Path

import environ

# Base directory 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ENV 환경변수 설정
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

# 사용자 지정 환경변수
NETFLIX_ID = env.str('NETFLIX_ID')
NETFLIX_PW = env.str('NETFLIX_PW')
TVING_ID = env.str('TVING_ID')
TVING_PW = env.str('TVING_PW')
AWS_REGION = env.str('AWS_REGION')
AWS_BUCKET_NAME = env.str('AWS_BUCKET_NAME')
AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY')

AWS_S3_BASE_URL = env.str('AWS_S3_BASE_URL')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

DEBUG = env('DEBUG')

# Host 설정
ALLOWED_HOSTS = env.str('ALLOWED_HOSTS').split(',')

# CSRF Trusted Token
CSRF_TRUSTED_ORIGINS = env.str('CSRF_TRUSTED_ORIGINS').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Custom App
    'rest_framework',
    'app.api',
    'app.database',
    'app.builder',
    'app.content',
    'app.utils',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # TEMPLATES 경로 설정
            os.path.join(BASE_DIR, 'templates'),
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

WSGI_APPLICATION = 'config.wsgi.application'


# 데이터베이스 Connection 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER_NAME'),
        'PASSWORD': env('DB_USER_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'CONN_MAX_AGE': 60
    }
}


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


# Django Rest Framework 설정
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ]
}


# Internationalization
LANGUAGE_CODE = env('LANGUAGE_CODE')

TIME_ZONE = env('TIME_ZONE')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Static Root
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# STATIC 경로 설정
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 로그인 성공 시 자동으로 이동할 URL
LOGIN_REDIRECT_URL = '/dashboard/'

# 로그아웃 성공 시 자동으로 이동할 URL
LOGOUT_REDIRECT_URL = '/login/'

# 로깅 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'test': {
            'format': u'%(asctime)s [%(levelname)-8s] %(funcName)s - %(message)s [%(pathname)s:%(lineno)d] ',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'level': env.str('LOG_LEVEL'),
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(env.str('LOG_PATH'), f'log-{datetime.today().date()}.log'),
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'test',
        },
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['file'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['file'],
            'propagate': False,
        },
    },
}
log = logging.getLogger('django')
