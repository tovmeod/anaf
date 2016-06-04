"""
Service Support: module definition
"""
from anaf.services.cron import tickets_escalate
PROPERTIES = {
    'title': 'Service Support',
    'details': 'Service delivery and support management',
    'url': '/services/',
    'system': False,
    'type': 'major'
}

URL_PATTERNS = [
    '^/services/',
]

#
# Cron
#


CRON = [tickets_escalate]
