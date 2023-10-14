from .models import Email
from rest_framework import serializers


class Emailserializer(serializers.ModelSerializer):
    
    
    class Meta:
          model = Email
          fields = '__all__'
    
          extra_kwargs = { 
            "email": {"required": True},
            "role": {"required": True},
         
            } 
        
     