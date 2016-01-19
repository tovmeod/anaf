"""
Sales: module definition
"""

PROPERTIES = {
    'title': 'Sales & Stock',
    'details': 'Sales and Client Relationship Management',
    'url': '/sales/',
    'system': False,
    'type': 'major'
}

URL_PATTERNS = [
    '^/sales/',
]

# Temporarily disabled cron due to failing .currency setting
# from anaf.sales.cron import subscription_check
# CRON = [subscription_check]
