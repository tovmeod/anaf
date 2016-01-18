"""
Sales Cron jobs
"""
from treeio.sales.models import Subscription


def subscription_check():
    "Automatically depreciate assets as per their depreciation rate"

    subscriptions = Subscription.objects.all()
    for subscription in subscriptions:
        subscription.check_status()
