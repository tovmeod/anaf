"""
Finance: module definition
"""

PROPERTIES = {
    'title': 'Finance',
    'details': 'Manage finance',
    'url': '/finance/',
    'system': False,
    'type': 'minor',
}


URL_PATTERNS = [
    '^/finance/',
]


from cron import assets_depreciate

CRON = [assets_depreciate]
