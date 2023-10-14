from django.contrib import admin
from apps.emails.models import Email

class EmailAdmin(admin.ModelAdmin):
    list_display = ("email","role",)
admin.site.register(Email,EmailAdmin)



