import logging.config

from django.utils.log import DEFAULT_LOGGING
from environ import Env
from environ import Path

# Set Environment
env = Env(
    DEBUG=(bool, False),
    DEFAULT_FROM_EMAIL=(str, 'webmaster@localhost'),
    TIME_ZONE=(str, 'US/Mountain'),
    EMAIL_URL=(str, 'smtp://localhost:1025'),
    REDIS_URL=(str, 'redis://localhost:6379/0'),
    LOGLEVEL=(str, 'INFO'),
)

root = Path(__file__) - 2

# Common
BASE_DIR = root()
SECRET_KEY = env("SECRET_KEY")
ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'
ADMINS = [
    ('admin', env("DEFAULT_FROM_EMAIL")),
]
SILENCED_SYSTEM_CHECKS = [
    'models.W042',
]

# Datetime
USE_TZ = True
DATE_FORMAT = 'Y-m-d'
TIME_FORMAT = 'H:i:s'
DATETIME_FORMAT = 'Y-m-d H:i:s'
TIME_ZONE = env("TIME_ZONE")

# HashIDs
HASHID_FIELD_SALT = env("HASHID_FIELD_SALT")

# Authentication
AUTH_USER_MODEL = 'app.User'
AUTHENTICATION_BACKENDS = [
    'app.backends.Auth0Backend',
]

LOGIN_URL = 'join'
LOGIN_REDIRECT_URL = 'account'
LOGOUT_REDIRECT_URL = 'index'

#Auth0
AUTH0_CLIENT_ID = env("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = env("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = env("AUTH0_DOMAIN")
AUTH0_TENANT = env("AUTH0_TENANT")

# Mailchimp
MAILCHIMP_API_KEY = env("MAILCHIMP_API_KEY")
MAILCHIMP_AUDIENCE_ID = env("MAILCHIMP_AUDIENCE_ID")

# Database
DATABASES = {
    'default': env.db()
}

# POSTGIS
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

# Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 20,
            },
            "REDIS_CLIENT_KWARGS": {
                "ssl_cert_reqs": None,
            },
        }
    },
}

# RQ
RQ_QUEUES = {
    'default': {
        'USE_REDIS_CACHE': 'default',
        'ASYNC': True,
    },
}
RQ_SHOW_ADMIN_LINK = True

# Sessions
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_SERIALIZER = 'app.serializers.HashidJSONEncoder'

# Email
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_CONFIG = env.email_url('EMAIL_URL')
vars().update(EMAIL_CONFIG)

# Static File Management
STATIC_ROOT = root('staticfiles')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'
WHITENOISE_USE_FINDERS = True

# Media File Management
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_ROOT = root('mediafiles')
MEDIA_URL = '/media/'
CLOUDINARY_URL = env("CLOUDINARY_URL")
CLOUDINARY_NAME = CLOUDINARY_URL.rpartition("@")[2]


# Google
GOOGLE_API_KEY = env("GOOGLE_API_KEY")

# Voter API
VOTER_API_KEY = env("VOTER_API_KEY")
VOTER_API_HOST = env("VOTER_API_HOST")


# Facebook
FACEBOOK_CLIENT_ID = env("FACEBOOK_CLIENT_ID")

# Phone Numbers
PHONENUMBER_DB_FORMAT = 'NATIONAL'
PHONENUMBER_DEFAULT_REGION = 'US'

# Sentry
SENTRY_DSN = env("SENTRY_DSN")
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT")
SENTRY_RELEASE = env("HEROKU_SLUG_COMMIT")
SENTRY_CONFIG = {
    'send_default_pii': True,
}

# PostHog
POSTHOG_API_KEY = env("POSTHOG_API_KEY")
POSTHOG_HOST = env("POSTHOG_HOST")

# Bootstrap
BOOTSTRAP4 = {
    "css_url": {
        "href": "https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css",
        "integrity": "sha384-B0vP5xmATw1+K9KRQjQERJvTumQW0nPEzvF6L/Z6nronJ3oUOFUFpCjEUQouq2+l",
        "crossorigin": "anonymous",
    },
    "javascript_url": {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.min.js",
        "integrity": "sha384-+YQ4JLhjyBLPDQt//I+STsc9iw4uQqACwlvpslubQzn4u2UU2UFM80nGisd026JF",
        "crossorigin": "anonymous",
    },
    "jquery_url": {
        "url": "https://code.jquery.com/jquery-3.5.1.min.js",
        "integrity": "sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0=",
        "crossorigin": "anonymous",
    },
    "jquery_slim_url": {
        "url": "https://code.jquery.com/jquery-3.5.1.slim.min.js",
        "integrity": "sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj",
        "crossorigin": "anonymous",
    },
    "popper_url": {
        "url": "https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js",
        "integrity": "sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN",
        "crossorigin": "anonymous",
    },
    "theme_url": None,
    'javascript_in_head': True,
    'include_jquery': 'slim',
}

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Templating
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            root('templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'app.context_processors.avatar',
                'app.context_processors.metrics',
            ],
        },
    },
]

# Logging
LOGGING_CONFIG = None
LOGLEVEL = env("LOGLEVEL")
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        # default for all undefined Python modules
        '': {
            'level': 'WARNING',
            'handlers': [
                'console',
            ],
        },
        'app': {
            'level': LOGLEVEL,
            'handlers': [
                'console',
            ],
            'propagate': False,
        },
        # Prevent noisy modules from logging to Sentry
        # 'noisy_module': {
        #     'level': 'ERROR',
        #     'handlers': ['console'],
        #     'propagate': False,
        # },
        # Default runserver request logging
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    },
})

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.gis',
    'django_rq',
    'reversion',
    'fsm_admin',
    'cloudinary',
    'bootstrap4',
    'phonenumber_field',
    'app',
]
