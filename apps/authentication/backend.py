from uuid import UUID

from apps.common.utils import get_object
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import HTTP_HEADER_ENCODING, authentication

from apps.authentication.exceptions import AuthenticationFailed, InvalidToken
from apps.token.models import AccessToken

AUTH_HEADER_TYPE_BYTES = {
    h.encode(HTTP_HEADER_ENCODING) for h in settings.AUTH_HEADER_TYPES
}


class Authentication(authentication.BaseAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """

    www_authenticate_realm = "api"
    media_type = "application/json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token_object = self.get_validated_token(raw_token)

        return self.get_user(validated_token_object), raw_token

    def authenticate_header(self, request):
        return '{} realm="{}"'.format(
            settings.AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def get_header(self, request):
        """
        Extracts the header containing the token from the given
        request.
        """
        header = request.META.get(settings.AUTH_HEADER_NAME)

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_raw_token(self, header):
        """
        Extracts an unvalidated token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] not in AUTH_HEADER_TYPE_BYTES:
            # Assume the header does not contain a token
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                _("Authorization header must contain two space-delimited values"),
                code="bad_authorization_header",
            )

        return parts[1]

    def get_validated_token(self, raw_token):
        """
        Validates a token and returns a validated token
        wrapper object.
        """
        messages = []

        try:
            token = get_object(AccessToken, token=UUID(hex=raw_token.decode()))
        except ValueError:
            raise InvalidToken(
                {
                    "detail": _("Given token not valid for any token type"),
                }
            )
        if (
            not token
            or token.exp < timezone.now()
            or token.validity == AccessToken.TokenValidity.INVALID
        ):
            raise InvalidToken(
                {
                    "detail": _("Given token not valid for any token type"),
                    "messages": messages,
                }
            )
        return token

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """

        try:
            user = validated_token.user
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        if not user.is_active:
            raise AuthenticationFailed(_("User is inactive"), code="user_inactive")

        return user


class MyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = (
        "apps.authentication.backend.Authentication"  # full import path OR class ref
    )
    name = "Authentication"  # name used in the schema

    def get_security_definition(self, auto_schema):
        return {
            "type": "bearer token",
            "in": "header",
            "name": "Bearer",
        }
