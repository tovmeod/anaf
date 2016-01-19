"""
Core: module definition
"""

PROPERTIES = {
    'title': 'Administration',
    'details': 'Core Administration',
    'url': '/admin/',
    'system': True,
    'type': 'user',
}

URL_PATTERNS = [
    '^/admin/',
]

# from anaf.core.cron import email_reply
# CRON = [email_reply, ]
CRON = []
