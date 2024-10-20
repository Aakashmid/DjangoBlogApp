
from pathlib import Path
import os
import dj_database_url # for production env


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8kbo$_-*8irf^50#5kdmn4=lm)o*w*7=a7*$git!+9ie-u$qyf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=False if os.environ.get('DEBUG') else True

APPEND_SLASH = True

ALLOWED_HOSTS = ['127.0.0.1']


# Application definitions

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'App',  
    'django_summernote',
    'debug_toolbar',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

]

ROOT_URLCONF = 'Project_Blog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'App.context_processors.BlogUser_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'Project_Blog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }     
}

               
# DATABASES = {
#     'default': dj_database_url.parse('postgresql://blogblenddb_zq2o_user:vyOylQcW4RE0lYKxXspKOAnXdgciZ0Fm@dpg-cqd8uuhu0jms73ebgak0-a.singapore-postgres.render.com/blogblenddb_zq2o', conn_max_age=600)   # use conn_max_age so that connection from  db remain for given time
#     }



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#### Added manually   ####
if  DEBUG:
    STATICFILES_DIRS=[
    BASE_DIR /'static'
    ]
    WHITENOISE_AUTOFRESH=True


# debug toolbar setting
INTERNAL_IPS = [
    '127.0.0.1',
]



MEDIA_ROOT=os.path.join(BASE_DIR,'media')
MEDIA_URL="/media/"
X_FRAME_OPTIONS='SAMEORIGIN'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600





### Settings configuration for production

if not DEBUG: 
    STATIC_ROOT=BASE_DIR /'staticfiles'
    # Compress and cache static files for production
    # STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    SECRET_KEY=os.environ.get('SECRET_KEY')
    # Replace the SQLite DATABASES configuration with PostgreSQL:
    DB_URL=os.environ.get('DATABASE_URL')
    DATABASES = {
    'default': dj_database_url.parse(DB_URL,conn_max_age=600)
    }
    if os.environ.get('ALLOWED_HOSTS'):
        ALLOWED_HOSTS+=os.environ.get('ALLOWED_HOSTS').split(',')

        
if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'myapp': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }