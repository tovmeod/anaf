"""
Knowledge management: admin page
"""
from models import KnowledgeFolder, KnowledgeItem, KnowledgeCategory
from django.contrib import admin


class KnowledgeFolderAdmin(admin.ModelAdmin):

    """ Knowledge type admin """
    list_display = ('name', 'details')
    search_fields = ['name']


class KnowledgeItemAdmin(admin.ModelAdmin):

    """ Knowledge item admin """
    list_display = ('name', 'folder', 'category', 'body')
    search_fields = ['name']


class KnowledgeCategoryAdmin(admin.ModelAdmin):

    """ Knowledge category admin """
    list_display = ('name', 'details')
    search_fields = ['name']

admin.site.register(KnowledgeFolder, KnowledgeFolderAdmin)
admin.site.register(KnowledgeItem, KnowledgeItemAdmin)
admin.site.register(KnowledgeCategory, KnowledgeCategoryAdmin)
