"""
API admin definitions
"""

from django.contrib import admin
from treeio.core.api.models import Consumer, Token, Nonce

admin.site.register(Consumer)
admin.site.register(Token)
admin.site.register(Nonce)
