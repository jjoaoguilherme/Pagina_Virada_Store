from pathlib import Path
import os
from dotenv import load_dotenv

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis do .env (apenas em ambiente local)
load_dotenv(BASE_DIR / '.env')

# Detecta ambiente: produção ou desenvolvimento
TARGET_ENV = os.getenv('TARGET_ENV', 'dev')
NOT_PROD = not TARGET_ENV.lower().startswith('prod')

# Chave secreta
SECRET_KEY = os.getenv('SECRET_KEY', 'chave-insegura-dev')

# Aviso em modo dev
if NOT_PROD and SECRET_KEY == 'chave-insegura-dev':
    print("⚠️ ATENÇÃO: Você está usando a SECRET_KEY padrão em modo de desenvolvimento.")

# Modo debug
DEBUG = os.getenv('DEBUG', 'True' if NOT_PROD else 'False').lower() in ['true', '1', 't']

# Hosts permitidos
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1 localhost").split()

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split() if not NOT_PROD else []

# Redirecionamento HTTPS
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() in ['true', '1', 't']
if SECURE_SSL_REDIRECT:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# URLs de redirecionamento de login/logout
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# Aplicações instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'forum',
    'widget_tweaks',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs do projeto
ROOT_URLCONF = 'Pagina_Virada_Store.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'base',       # só o base.html
            BASE_DIR / 'templates',  # todos os outros .html
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'forum.context_processors.cart_item_count',
            ],
        },
    },
]
# WSGI
WSGI_APPLICATION = 'Pagina_Virada_Store.wsgi.application'

# Banco de dados
if NOT_PROD:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    required_vars = ['DBNAME', 'DBUSER', 'DBPASS', 'DBHOST']
    for var in required_vars:
        if not os.getenv(var):
            raise Exception(f"Variável de ambiente obrigatória ausente: {var}")

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DBNAME'),
            'USER': os.getenv('DBUSER'),
            'PASSWORD': os.getenv('DBPASS'),
            'HOST': os.getenv('DBHOST'),
            'PORT': '5432',
            'OPTIONS': {'sslmode': 'require'},
        }
    }

# Validação de senhas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
USE_L10N = True

# Arquivos estáticos
STATIC_URL = os.environ.get('DJANGO_STATIC_URL', '/static/')
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Arquivos de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Chave primária padrão
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logs para produção
if not NOT_PROD:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
from pathlib import Path
import os
from dotenv import load_dotenv

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis do .env (apenas em ambiente local)
load_dotenv(BASE_DIR / '.env')

# Detecta ambiente: produção ou desenvolvimento
TARGET_ENV = os.getenv('TARGET_ENV', 'dev')
NOT_PROD = not TARGET_ENV.lower().startswith('prod')

# Chave secreta
SECRET_KEY = os.getenv('SECRET_KEY', 'chave-insegura-dev')

# Aviso em modo dev
if NOT_PROD and SECRET_KEY == 'chave-insegura-dev':
    print("⚠️ ATENÇÃO: Você está usando a SECRET_KEY padrão em modo de desenvolvimento.")

# Modo debug
DEBUG = os.getenv('DEBUG', 'True' if NOT_PROD else 'False').lower() in ['true', '1', 't']

# Hosts permitidos
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1 localhost").split()

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split() if not NOT_PROD else []

# Redirecionamento HTTPS
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() in ['true', '1', 't']
if SECURE_SSL_REDIRECT:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# URLs de redirecionamento de login/logout
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# Aplicações instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'forum',
    'widget_tweaks',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs do projeto
ROOT_URLCONF = 'Pagina_Virada_Store.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'base'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'forum.context_processors.cart_item_count',

            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'Pagina_Virada_Store.wsgi.application'

# Banco de dados
if NOT_PROD:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    required_vars = ['DBNAME', 'DBUSER', 'DBPASS', 'DBHOST']
    for var in required_vars:
        if not os.getenv(var):
            raise Exception(f"Variável de ambiente obrigatória ausente: {var}")

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DBNAME'),
            'USER': os.getenv('DBUSER'),
            'PASSWORD': os.getenv('DBPASS'),
            'HOST': os.getenv('DBHOST'),
            'PORT': '5432',
            'OPTIONS': {'sslmode': 'require'},
        }
    }

# Validação de senhas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
USE_L10N = True

# Arquivos estáticos
STATIC_URL = os.environ.get('DJANGO_STATIC_URL', '/static/')
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Arquivos de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Chave primária padrão
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logs para produção
if not NOT_PROD:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
