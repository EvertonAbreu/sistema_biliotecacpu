from pathlib import Path
import os
import dj_database_url

# ==============================
# BASE
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
# SEGURANÇA
# ==============================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-chave-apenas-desenvolvimento"
)

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost,.onrender.com"
).split(",")

# ==============================
# APLICAÇÕES
# ==============================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "core",
]

# ==============================
# MIDDLEWARE
# ==============================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "biblioteca.urls"
WSGI_APPLICATION = "biblioteca.wsgi.application"

# ==============================
# TEMPLATES
# ==============================

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
                "django.template.context_processors.media",
            ],
        },
    },
]

# ==============================
# BANCO DE DADOS
# ==============================

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ==============================
# VALIDAÇÃO DE SENHA
# ==============================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==============================
# INTERNACIONALIZAÇÃO
# ==============================

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ==============================
# ARQUIVOS ESTÁTICOS
# ==============================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = []
static_dir = BASE_DIR / "static"
if static_dir.exists():
    STATICFILES_DIRS.append(static_dir)

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"# ==============================
# ARQUIVOS DE MÍDIA
# ==============================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ==============================
# AUTENTICAÇÃO
# ==============================

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==============================
# CORS
# ==============================

CORS_ALLOW_ALL_ORIGINS = DEBUG

# ==============================
# PRODUÇÃO (RENDER)
# ==============================

if not DEBUG:

    # ESSENCIAL para o Render reconhecer HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "SAMEORIGIN"



