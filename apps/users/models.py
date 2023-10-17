from apps.common.models import BaseModel, CustomID
from django.apps import apps
from django.contrib.auth import get_backends, load_backend
from django.contrib.auth.base_user import BaseUserManager as BUM
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BUM):
    def create_user(
        self,
        primary_email=None,
        username=None,
        password=None,
        is_staff=False,
        **extra_fields
    ):
        extra_fields.setdefault("is_superuser", False)

        # validation
        if not primary_email:
            raise ValidationError(_("User must have primary_email"))
        primary_email = self.normalize_email(primary_email)
        if not username:
            raise ValidationError(_("User must have username"))
        if not password:
            raise ValidationError(_("User must have to set password"))

        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)

        # creating user
        user = self.model(
            username=username,
            primary_email=primary_email,
            is_staff=is_staff,
            **extra_fields
        )
        user.set_password(password)

        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(
        self, primary_email=None, username=None, password=None, **extra_fields
    ):
        if not username:
            raise ValueError(_("You must provide an username"))
        if not primary_email:
            raise ValueError(_("You must provide an email"))

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")

        return self.create_user(
            username=username,
            primary_email=primary_email,
            password=password,
            **extra_fields
        )

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(CustomID, BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    # User Information ######

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
        null=True,
        blank=True,
    )
    password = models.CharField(_("password"), max_length=128, null=True, blank=True)
    primary_email = models.EmailField(_("Email"), unique=True, null=True, blank=True)
    contact_number = PhoneNumberField(
        verbose_name=_("Contact Number"), unique=True, blank=True, null=True
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
        null=True,
        blank=True,
    )
    is_staff = models.BooleanField(default=False, null=True, blank=True)

    EMAIL_FIELD = "primary_email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["primary_email", "password", "contact_number"]
    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        permissions = (
            ("can_login_web", "To Login Webpanel"),
            ("can_login_app", "To Login App"),
        )

    @property
    def date_joined(self):
        return self.created_at

    def __str__(self):
        return str(self.username)
