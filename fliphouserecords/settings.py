from pathlib import Path
import os
import mimetypes
import dj_database_url
from storages.backends.s3boto3 import S3Boto3Storage

# === Base Directory ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Security & Environment ===
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

# === Installed Apps ===
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "releases",
    "storages",
]

# === Middleware (WhiteNoise removed) ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# === Templates ===
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# === Database ===
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# === AWS S3 Config ===
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")

AWS_S3_ADDRESSING_STYLE = "virtual"  # Use virtual-hosted–style URLs
AWS_S3_FILE_OVERWRITE = False        # Don’t overwrite files with same name
AWS_DEFAULT_ACL = "public-read"      # Make uploaded files public
AWS_QUERYSTRING_AUTH = False         # Don't append auth tokens to URLs





# === Static / Media Files ===
STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/"
STATICFILES_STORAGE = "storage_backends.StaticStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"
DEFAULT_FILE_STORAGE = "storage_backends.MediaStorage"

# === Authentication & Passwords ===
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# === Time & Language ===
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === Production Security ===
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# === MIME Fixes for S3
mimetypes.add_type("image/png", ".png", True)
mimetypes.add_type("image/x-icon", ".ico", True)

# === URL Routing
ROOT_URLCONF = "fliphouserecords.urls"
WSGI_APPLICATION = "fliphouserecords.wsgi.application"
