from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.token.models import AccessToken
# Register your models here.


@admin.register(AccessToken)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token_hidden", "validity", "created_at", "updated_at")
    readonly_fields = ('token_hidden',)
    exclude = ('token',)
    
    def token_hidden(self, obj):
        token = obj.token
        if token:
            return mark_safe('*' * len(str(token)))
        return ''
    
    token_hidden.short_description = 'Token'
