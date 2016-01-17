"""
Multitenancy settings
"""

from django.conf import LazySettings
from pandora import box

DEFAULTS = {
    'MODULE_IDENTIFIER': 'hmodule',
    'RESPONSE_FORMATS': {
                'html': 'text/html',
                'mobile': 'text/html',
                'json': 'text/plain',
                # 'json': 'application/json',
                'ajax': 'text/plain',
                # 'ajax': 'application/json',
                'csv': 'text/csv',
                'xls': 'text/xls',
                'pdf': 'application/pdf',
                'rss': 'application/rss+xml',
    },
    'EMAIL_SERVER': '127.0.0.1',
    'IMAP_SERVER': '',
    'EMAIL_USERNAME': None,
    'EMAIL_PASSWORD': None,
    'EMAIL_FROM': 'noreply@anaf',
    'DEFAULT_SIGNATURE': """
Thanks!
The Anaf Team
            """,
    'DEFAULT_USER_ID': 1,
    'DEFAULT_PERMISSIONS': 'everyone'
}


class Settings(LazySettings):

    def __getattr__(self, key):
        if key in box:
            return box[key]
        else:
            if key.startswith('ANAF_'):
                name = key[5:]  # removes prefix
                if name in DEFAULTS:
                    return getattr(super(Settings, self), key, DEFAULTS[name])
            return super(Settings, self).__getattr__(key)

settings = Settings()
