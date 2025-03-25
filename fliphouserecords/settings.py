from pathlib import Path
import os
import dj_database_url
import mimetypes
from storages.backends.s3boto3 import S3Boto3Storage  # ✅ FIX: This was missing

# === Base Directory ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Secret Key / Environment Vars ===
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# === Installed Apps ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'releases',
    'storages',  # for AWS S3 support
]

# === Middleware (WhiteNoise removed) ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === Templates ===
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
            ],
        },
    },
]

# === Database (Render PostgreSQL or fallback to SQLite) ===
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True
    )
}

# === AWS S3 Settings ===
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False  # ⛔ No signed URLs for static/media
AWS_DEFAULT_ACL = "public-read"

# === Custom S3 Storage Backends ===
class StaticStorage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"

class MediaStorage(S3Boto3Storage):
    location = ""
    file_overwrite = False
    default_acl = "public-read"

# === Static Files (served from S3) ===
STATICFILES_STORAGE = "fliphouserecords.settings.StaticStorage"
STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# === Media Files (uploads served from S3) ===
DEFAULT_FILE_STORAGE = "fliphouserecords.settings.MediaStorage"
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"

# === Authentication, Passwords, Security ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === Locale & Timezone ===
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === Security for Production ===
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# === Fix MIME types (S3 requires explicit types sometimes)
mimetypes.add_type("image/png", ".png", True)
mimetypes.add_type("image/x-icon", ".ico", True)

# === Routing
ROOT_URLCONF = "fliphouserecords.urls"
WSGI_APPLICATION = "fliphouserecords.wsgi.application"
