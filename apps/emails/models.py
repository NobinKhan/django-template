from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class Email(models.Model):
    
    email =  models.EmailField(_('Email'), unique=True, null=True, blank=True)
    role =  models.CharField(max_length=180,null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
  
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                name="unique_email_address"
            )
        ]
    
    def __str__(self):
        return f"{self.email}"