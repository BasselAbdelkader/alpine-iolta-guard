"""
Django PRODUCTION settings for trust_account_project.

This file contains production-ready settings with security hardening.
"""
import os
import json
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load configuration from account.json
def load_config():
    config_path = BASE_DIR.parent / 'account.json'
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

CONFIG = load_config()

# ============================================================================
# SECURITY SETTINGS - PRODUCTION
# ============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', CONFIG.get('application', {}).get('secret_key'))
if not SECRET_KEY or SECRET_KEY == 'django-insecure-fallback-key':
    raise ValueError("DJANGO_SECRET_KEY must be set in environment or account.json for production")

# DEBUG MODE - MUST BE FALSE IN PRODUCTION
DEBUG = False
ENABLE_STATIC_FILES = True

# Force static file serving even with DEBUG=False
FORCE_SERVE_STATIC = True

# ALLOWED HOSTS - Configure for your production domain
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') or CONFIG.get('application', {}).get('allowed_hosts', [])
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be configured for production")

# ============================================================================
# APPLICATION DEFINITION
# ============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Django REST Framework
    'rest_framework',
    'corsheaders',
    'django_filters',
    # Local apps
    'apps.dashboard',
    'apps.clients',
    'apps.vendors',
    'apps.bank_accounts',
    'apps.settlements',
    'apps.reports',
    'apps.settings',
    'apps.checks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'trust_account_project.security.BruteForceProtectionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'trust_account_project.middleware.NoCacheAfterLogoutMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'trust_account_project.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'trust_account_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'apps' / 'dashboard' / 'templates',
            BASE_DIR / 'apps' / 'clients' / 'templates',
            BASE_DIR / 'apps' / 'vendors' / 'templates',
            BASE_DIR / 'apps' / 'bank_accounts' / 'templates',
            BASE_DIR / 'apps' / 'settlements' / 'templates',
            BASE_DIR / 'apps' / 'reports' / 'templates',
            BASE_DIR / 'apps' / 'settings' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'trust_account_project.context_processors.law_firm_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'trust_account_project.wsgi.application'

# ============================================================================
# DATABASE CONFIGURATION - PRODUCTION
# ============================================================================

DB_CONFIG = CONFIG.get('database', {})
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', DB_CONFIG.get('db_name')),
        'USER': os.environ.get('DB_USER', DB_CONFIG.get('db_user')),
        'PASSWORD': os.environ.get('DB_PASSWORD', DB_CONFIG.get('db_password')),
        'HOST': os.environ.get('DB_HOST', DB_CONFIG.get('db_host')),
        'PORT': int(os.environ.get('DB_PORT', DB_CONFIG.get('db_port', 5432))),
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Stronger minimum length for production
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================================================
# STATIC FILES - PRODUCTION
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise configuration for efficient static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# AUTHENTICATION & SESSION - PRODUCTION
# ============================================================================

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# Session settings - PRODUCTION SECURE
SESSION_COOKIE_AGE = 28800  # 8 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_SAVE_EVERY_REQUEST = True

# Enhanced Authentication Backend
AUTHENTICATION_BACKENDS = [
    'trust_account_project.security.SecureAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ============================================================================
# SECURITY HEADERS - PRODUCTION HARDENED
# ============================================================================

# HTTPS/SSL Settings
SECURE_SSL_REDIRECT = True  # Force HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # For reverse proxy

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Browser Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Content Security Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Cookie Security
CSRF_COOKIE_SECURE = True  # HTTPS only
CSRF_COOKIE_HTTPONLY = True  # No JavaScript access
CSRF_COOKIE_SAMESITE = 'Lax'

# ============================================================================
# BRUTE FORCE PROTECTION
# ============================================================================

BRUTE_FORCE_MAX_ATTEMPTS = 5           # Max failed attempts before blocking
BRUTE_FORCE_LOCKOUT_DURATION = 900     # Block duration in seconds (15 minutes)
BRUTE_FORCE_COOLDOWN = 60               # Rapid attempt cooldown (1 minute)

# ============================================================================
# INPUT VALIDATION
# ============================================================================

MAX_INPUT_LENGTH = 10000
ENABLE_INPUT_SANITIZATION = True

# ============================================================================
# CACHING - PRODUCTION
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 900,
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
        }
    }
}

# ============================================================================
# LOGGING - PRODUCTION
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django_error.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}

# ============================================================================
# REST FRAMEWORK - PRODUCTION SECURED
# ============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.api.authentication.CsrfExemptSessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # REQUIRE AUTHENTICATION
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',  # JSON only (no browsable API)
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'EXCEPTION_HANDLER': 'trust_account_project.exceptions.custom_exception_handler',
}

# ============================================================================
# CORS CONFIGURATION - PRODUCTION RESTRICTED
# ============================================================================

# Only allow your production frontend domain
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') or CONFIG.get('application', {}).get('cors_origins', [])

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ============================================================================
# JWT CONFIGURATION - PRODUCTION
# ============================================================================

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ============================================================================
# ADMIN INTERFACE - PRODUCTION (Restricted)
# ============================================================================

# Disable admin in production or restrict to internal IPs
ADMIN_ENABLED = os.environ.get('ADMIN_ENABLED', 'False').lower() == 'true'

# If admin is needed, restrict to internal IPs
INTERNAL_IPS = os.environ.get('INTERNAL_IPS', '').split(',')

# ============================================================================
# DATABASE CONNECTION SECURITY
# ============================================================================

# Hide database from public access - ensure firewall rules are in place
# Database should only be accessible from application servers
# Recommendation: Use private network or VPN for database access

print("=" * 80)
print("PRODUCTION SETTINGS LOADED")
print("=" * 80)
print(f"DEBUG: {DEBUG}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"SECURE_SSL_REDIRECT: {SECURE_SSL_REDIRECT}")
print(f"SESSION_COOKIE_SECURE: {SESSION_COOKIE_SECURE}")
print(f"CSRF_COOKIE_SECURE: {CSRF_COOKIE_SECURE}")
print(f"ADMIN_ENABLED: {ADMIN_ENABLED}")
print("=" * 80)
