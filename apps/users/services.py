from typing import Optional

from django.db import transaction
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

from apps.users.models import User
from apps.common.services import model_update



def create_user(*, username: str = None, primary_email: str = None, password=None, **extra_fields) -> User:
    # data cleaning
    groups = None
    if extra_fields.get('groups'):
        groups = Group.objects.filter(name__in=extra_fields.pop('groups'))

    # user create conditions
    # Create user
    user = User.objects.create_user(
        username=username,
        primary_email=primary_email, 
        is_staff=False, 
        password=password,
        **extra_fields
    )

    # set permissions
    if groups:
        if isinstance(groups, Group):
            user.groups.add(groups)
        else:
            user.groups.set(groups)

    subject = "New Account Created - Your Login Credentials" 
    message =  f"Welcome to Asset Verification System. We are writing to inform you that we have created a new account for you on our platform. Below are your login credentials: \n\nUsername: {username} \nPassword: {password} \n\nPlease keep this information confidential and do not share it with anyone else. You can use these credentials to log in to your account.\n\nThank you."
    from_email = "info@carebox.com"

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[user.primary_email],
        fail_silently=False,
    )

    return user



@transaction.atomic
def user_update(*, user: User, data) -> User:
    non_side_effect_fields = ["username", "password", "primary_email", "contact_number", "groups"]
    
    if data.get('groups'):
        data.update(
            groups=Group.objects.filter(name__in=data.pop('groups'))
        )
    password = None
    if data.get('password'):
        password = data.pop('password')

    user, has_updated = model_update(instance=user, fields=non_side_effect_fields, data=data)
    
    if password:
        User.objects.filter(id=user.id).update(password=make_password(password))
        has_updated = True

        # send email on password change
        subject = "Account Updated - Your Login Credentials" 
        message =  f"Welcome to Asset Verification System. We are writing to inform you that your account has been updated recently. Below are your login credentials: \n\nUsername: {user.username} \nPassword: {password} \n\nPlease keep this information confidential and do not share it with anyone else. You can use these credentials to log in to your account.\n\nThank you."
        from_email = "info@carebox.com"
        print(message)
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[user.primary_email],
            fail_silently=False,
        )
    return user, has_updated


