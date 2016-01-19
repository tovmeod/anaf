"""
Finance: admin page
"""
from models import Transaction, Liability, Category
from django.contrib import admin


class TransactionAdmin(admin.ModelAdmin):

    """ Transaction admin """
    list_display = ('name', 'details')
    search_fields = ['name']


class LiabilityAdmin(admin.ModelAdmin):

    """ Liability admin """
    list_display = ('name', 'details')
    search_fields = ['name']


class CategoryAdmin(admin.ModelAdmin):

    """ Category admin """
    list_display = ('name', 'id')
    search_fields = ['name']

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Liability, LiabilityAdmin)
admin.site.register(Category, CategoryAdmin)
