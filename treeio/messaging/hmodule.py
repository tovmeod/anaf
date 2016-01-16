"""
Messaging: module definition
"""

PROPERTIES = {
    'title': 'Messaging',
    'details': 'Sending messages',
    'url': '/messaging/',
    'system': False,
    'type': 'minor',
}

URL_PATTERNS = [
    '^/messaging/',
]


#
# Cron
#
from treeio.messaging.cron import process_email

CRON = [process_email]
