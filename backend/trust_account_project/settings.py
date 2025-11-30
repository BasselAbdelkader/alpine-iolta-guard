"""
Django settings for trust_account_project.
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

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG.get('application', {}).get('secret_key', 'django-insecure-fallback-key')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG MODE - SET TO FALSE FOR PRODUCTION
DEBUG = True  # PRODUCTION: Set to False
ENABLE_STATIC_FILES = True  # Enable static files even with DEBUG=False

# For development with Docker, force static file serving
FORCE_SERVE_STATIC = True

ALLOWED_HOSTS = CONFIG.get('application', {}).get('allowed_hosts', ['localhost', '127.0.0.1', '0.0.0.0', '138.68.109.92', 'host.docker.internal'])
# Production IP explicitly added
if '138.68.109.92' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('138.68.109.92')

# Application definition
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
    # 'apps.transactions',  # Consolidated into bank_accounts
    'apps.bank_accounts',
    'apps.settlements',
    'apps.reports',
    'apps.settings',
    'apps.checks',
    'apps.imports',  # Two-stage CSV import with approval workflow
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Django's built-in CSRF protection (sufficient)
    # REMOVED: 'trust_account_project.csrf_protection.AdvancedCSRFProtectionMiddleware' - Redundant with Django's CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'trust_account_project.threat_detection.AdvancedThreatDetectionMiddleware',  # SECURITY FIX: Brute force protection
    'trust_account_project.security.BruteForceProtectionMiddleware',
    'trust_account_project.api_hardening.APISecurityMiddleware',  # SECURITY FIX: API hardening
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
            # BASE_DIR / 'apps' / 'transactions' / 'templates',  # Consolidated
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

# Database configuration - prioritize environment variables over account.json
DB_CONFIG = CONFIG.get('database', {})
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', DB_CONFIG.get('db_name', 'bank_account_db')),
        'USER': os.environ.get('DB_USER', DB_CONFIG.get('db_user', 'bank_user')),
        'PASSWORD': os.environ.get('DB_PASSWORD', DB_CONFIG.get('db_password', 'secure_password_123')),
        'HOST': os.environ.get('DB_HOST', DB_CONFIG.get('db_host', 'bank_account_db')),
        'PORT': int(os.environ.get('DB_PORT', DB_CONFIG.get('db_port', 5432))),
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise configuration for static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login settings - no forced password change
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# Session settings
SESSION_COOKIE_AGE = 28800  # 8 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = None  # Allow cross-origin cookies for frontend-backend separation
SESSION_COOKIE_DOMAIN = None  # Allow cookies on any domain (localhost or production)
SESSION_SAVE_EVERY_REQUEST = True

# Security settings - Enhanced for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Additional security headers for production
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = False  # Set to True when HTTPS is enabled
SECURE_PROXY_SSL_HEADER = None  # Configure for reverse proxy if needed

# Content Security Policy - Basic configuration
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Enhanced Authentication Backend
AUTHENTICATION_BACKENDS = [
    'trust_account_project.security.SecureAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Brute Force Protection Settings
BRUTE_FORCE_MAX_ATTEMPTS = 5           # Max failed attempts before blocking
BRUTE_FORCE_LOCKOUT_DURATION = 900     # Block duration in seconds (15 minutes)
BRUTE_FORCE_COOLDOWN = 60               # Rapid attempt cooldown (1 minute)

# Enhanced Input Validation Settings
MAX_INPUT_LENGTH = 10000                # Maximum input field length
ENABLE_INPUT_SANITIZATION = True        # Enable automatic input sanitization

# Cache Configuration for Brute Force Protection (Redis-backed, persistent)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', '6379')}/1",
        'TIMEOUT': 900,  # 15 minutes default timeout
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'KEY_PREFIX': 'iolta_prod',  # Namespace for cache keys
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.api.authentication.CsrfExemptSessionAuthentication',  # Session auth without CSRF for API
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # PRODUCTION: Require authentication for all API requests
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',      # Unauthenticated users: 100 requests per hour
        'user': '1000/hour',     # Authenticated users: 1000 requests per hour
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8003",  # Local development nginx
    "http://localhost:8080",  # Local development nginx alternate port
    "http://138.68.109.92",   # Production server
    "http://138.68.109.92:80",  # Production server with explicit port
]

CORS_ALLOW_CREDENTIALS = True

# JWT Configuration
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
