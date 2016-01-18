"""
Finance Cron jobs
"""
from treeio.finance.models import Asset


def assets_depreciate():
    "Automatically depreciate assets as per their depreciation rate"

    assets = Asset.objects.all()
    for asset in assets:
        if not asset.trash:
            asset.set_current_value()
