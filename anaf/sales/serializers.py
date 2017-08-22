from rest_framework import serializers

from anaf.sales.models import SaleStatus, Product, SaleSource, Lead, Opportunity, SaleOrder, Subscription, \
    OrderedProduct
from anaf.serializers import common_exclude


class SaleStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SaleStatus
        exclude = common_exclude


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        exclude = common_exclude


class SaleSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SaleSource
        exclude = common_exclude


class LeadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lead
        exclude = common_exclude


class OpportunitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Opportunity
        exclude = common_exclude


class SaleOrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SaleOrder
        exclude = common_exclude


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subscription
        exclude = common_exclude


class OrderedProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OrderedProduct
        exclude = common_exclude
