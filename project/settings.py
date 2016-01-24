# -*- coding: utf-8 -*-

import os
from os import path
from whoosh import fields
import ConfigParser
import sys

BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))
CONFIG_FILE = 'anaf.ini'
USER_CONFIG_FILE = CONFIG_FILE
DEFAULT_CONFIG_FILE = path.join(BASE_DIR, CONFIG_FILE)
DEBUG = (True if 'DEBUG' not in os.environ else {'true': True, 'false': False}[os.environ['DEBUG'].lower()])
DEBUG = True
TEMPLATE_DEBUG = DEBUG

QUERY_DEBUG = False
QUERY_DEBUG_FULL = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS
DATABASES = {}
TESTING = 'test' in sys.argv or 'test_coverage' in sys.argv  # Covers regular testing and django-coverage

if TESTING:
    test_db = os.environ.get('DB', 'sqlite')
    if test_db == 'mysql':
        DATABASES = {'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'anaf',
            'USER': 'root',
            }}
    elif test_db == 'postgres':
        DATABASES = {'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'anaf',
            'USER': 'postgres',
        }}
    elif test_db == 'sqlite':
        DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
    elif test_db == 'mssql':
        DATABASES = {'default': {
            'ENGINE': 'sqlserver',
            'NAME': 'anaf_{0!s}'.format(os.environ.get('MC')),
            'USER': 'anaf',
            'PASSWORD': 'anaf',
            'HOST': '10.0.0.9',
    }}
    elif test_db == 'oracle':
        DATABASES = {'default': {
            'ENGINE': 'django.db.backends.oracle',
            'NAME': 'anaf',
            'USER': 'anaf',
            'PASSWORD': 'anaf',
        }}

    if os.environ.get('MC') == '1':
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
                'LOCATION': '127.0.0.1:11211',
                }
        }

    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)
    ANAF_API_AUTH_ENGINE = 'basic'
else:
    CONF = ConfigParser.ConfigParser()
    CONF.optionxform = str  # to preserve case for the options names
    CONF.read((DEFAULT_CONFIG_FILE, USER_CONFIG_FILE))
    DATABASES = {
        'default': dict(CONF.items('db'))
    }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-GB'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
FORMAT_MODULE_PATH = 'anaf.formats'

# OAUTH_DATA_STORE is needed for correct database setting up
# OAUTH_DATA_STORE = 'anaf.core.api.auth.store.store'

# Static files location
if not DEBUG:
    STATIC_URL = path.join(BASE_DIR, 'static/')
else:
    STATICFILES_DIRS = (
        path.join(BASE_DIR, 'anaf/static'),
    )
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(path.dirname(BASE_DIR), 'anaf/static')
STATIC_DOC_ROOT = os.path.join(BASE_DIR, 'anaf/static')
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'dajaxice.finders.DajaxiceFinder',
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(STATIC_DOC_ROOT, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/media/'

# Captcha Settings
CAPTCHA_FONT_SIZE = 30
CAPTCHA_LENGTH = 6
CAPTCHA_DISABLE = True
CAPTCHA_FOREGROUND_COLOR = '#333333'
CAPTCHA_NOISE_FUNCTIONS = []

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static-admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'z_#oc^n&z0c2lix=s$4+z#lsb9qd32qtb!#78nk7=5$_k3lq16'

# List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = (
#     'django.template.loaders.filesystem.load_template_source',
#     'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
# )
if DEBUG or TESTING:
    TEMPLATE_LOADERS = [
        'django.template.loaders.app_directories.Loader',
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.eggs.Loader',
    ]
else:
    TEMPLATE_LOADERS = [
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.app_directories.Loader',
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.eggs.Loader',
            )),
    ]

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    'django.contrib.messages.context_processors.messages',
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'anaf.core.middleware.user.AuthMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    "anaf.core.middleware.user.LanguageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    'django.middleware.common.CommonMiddleware',
    'johnny.middleware.LocalStoreClearMiddleware',
    'johnny.middleware.QueryCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    # 'anaf.core.middleware.domain.DomainMiddleware',
    'anaf.core.middleware.user.SSLMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'anaf.core.middleware.chat.ChatAjaxMiddleware',
    "django.contrib.messages.middleware.MessageMiddleware",
    "anaf.core.middleware.modules.ModuleDetect",
    "minidetector.Middleware",
    "anaf.core.middleware.user.CommonMiddleware",
    "anaf.core.middleware.user.PopupMiddleware",
)


ROOT_URLCONF = 'project.urls'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'anaf/templates'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django_websocket',
    'django.contrib.messages',
    'rest_framework',
    'anaf.account',
    'anaf.core',
    'anaf.core.api',
    'anaf.core.search',
    'anaf.documents',
    'anaf.events',
    'anaf.finance',
    'anaf.identities',
    'anaf.infrastructure',
    'anaf.knowledge',
    'anaf.messaging',
    'anaf.news',
    'anaf.projects',
    'anaf.reports',
    'anaf.sales',
    'anaf.services',
    'dajaxice',
    'dajax',
    'coffin',
    'captcha',
    'markup_deprecated',
)
try:
    import rosetta
    INSTALLED_APPS += ('rosetta',)
except ImportError:
    pass
if not DEBUG:
    INSTALLED_APPS += ('django.contrib.staticfiles',)

AUTH_PROFILE_MODULE = 'core.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'anaf.core.auth.HashBackend',
    'anaf.core.auth.EmailBackend',
)

# LDAP Configuration
# AUTH_LDAP_SERVER_URI = 'ldap://'
# AUTH_LDAP_BIND_DN = ""
# AUTH_LDAP_BIND_PASSWORD = ""
# AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com",
#        ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
# AUTH_LDAP_START_TLS = True


# LOCALE_PATHS = (BASE_DIR + "/anaf/locale",)

#
# Anaf Subcription settings
#

EVERGREEN_FREE_USERS = 3

USER_PRICE = 15

#
# Nuvius settings (for integration)
#
NUVIUS_URL = "http://nuvius.com"
NUVIUS_KEY = '28563.ff6ed93307fc398a52d312966c122660'
NUVIUS_SOURCE_ID = "28563"
NUVIUS_NEXT = "iframe"
NUVIUS_CHECK_USER_KEYS = True

NUVIUS_DATA_CACHE_LIFE = 600
CACHE_KEY_PREFIX = 'anaf_'

#
# Search index (Whoosh)
#
SEARCH_DISABLED = False
SEARCH_ENGINE = 'db'

WHOOSH_SCHEMA = fields.Schema(id=fields.ID(stored=True, unique=True),
                              name=fields.TEXT(stored=True),
                              type=fields.TEXT(stored=True),
                              content=fields.TEXT,
                              url=fields.ID(stored=True))

WHOOSH_INDEX = os.path.join(BASE_DIR, 'storage/search')

#
# CACHING
#
if not TESTING:
    try:
        import pylibmc
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
                'LOCATION': CONF.get('memcached', 'location'),
                }
        }
    except ImportError:
        import tempfile
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
                'LOCATION': tempfile.mkdtemp('django_cache'),
                }
        }

# CACHE_BACKEND="johnny.backends.locmem://"

JOHNNY_MIDDLEWARE_KEY_PREFIX = 'jc_anaf'

DISABLE_QUERYSET_CACHE = False

WKPATH = os.path.join(BASE_DIR, 'bin/wkhtmltopdf')
WKCWD = BASE_DIR

CHAT_LONG_POLLING = False
CHAT_TIMEOUT = 25  # response time if not new data
CHAT_TIME_SLEEP_THREAD = 25  # interval for "Delete inactive users"
CHAT_TIME_SLEEP_NEWDATA = 1  # time sleep in expectation of new data

MESSAGE_STORAGE = 'anaf.core.contrib.messages.storage.cache.CacheStorage'

# Dajaxice settings
DAJAXICE_MEDIA_PREFIX = "dajaxice"

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    # '.example.com', # Allow domain and subdomains
    # '.example.com.', # Also allow FQDN and subdomains
    ]

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# monkey patch because dajax still tries to import django simplejson
import json
import django.utils
django.utils.simplejson = json
