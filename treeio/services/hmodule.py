"""
Service Support: module definition
"""

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

from treeio.services.cron import tickets_escalate

CRON = [tickets_escalate]
