"""
Account: backend admin definitions
"""

from treeio.account.models import NotificationSetting, Notification
from django.contrib import admin


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'ntype', 'date_created')


class NotificationSettingAdmin(admin.ModelAdmin):

    "NotificationSetting backend definition"
    list_display = ('owner', 'ntype',)

admin.site.register(NotificationSetting, NotificationSettingAdmin)
admin.site.register(Notification, NotificationAdmin)
