from uuid import UUID

from apps.common.permissions import AddUser
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.token.models import AccessToken
from apps.token.services import create_token
from apps.users.models import User
from apps.users.services import create_user


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("style", {})
        kwargs["style"]["input_type"] = "password"
        kwargs["write_only"] = True
        super().__init__(*args, **kwargs)


class Login(APIView):
    serializer_class = None

    class InputSerializer(serializers.Serializer):
        username = serializers.CharField(required=True)
        password = PasswordField(required=True)

    def post(self, request):
        self.serializer_class = self.InputSerializer(data=request.data)
        self.serializer_class.is_valid(raise_exception=True)

        user = authenticate(request, **self.serializer_class.validated_data)
        if user is None:
            raise AuthenticationFailed(_("Invalid Credentials"))

        perpose = request.query_params.get("perpose")
        if not perpose or not user.has_perm(f"users.{perpose}"):
            raise AuthenticationFailed(_("Sorry, you don't have permission!"))

        update_last_login(None, user)
        access_token = create_token(user)

        return Response({"access_token": access_token})


class Register(APIView):
    permission_classes = [AddUser]
    serializer_class = None

    class InputSerializer(serializers.Serializer):
        username = serializers.CharField(required=True)
        email = serializers.EmailField(required=True)
        contact_number = PhoneNumberField(required=False)
        password = PasswordField(required=True)
        roles = serializers.ListField(
            child=serializers.CharField(
                required=True, allow_blank=False, allow_null=False
            ),
            required=False,
            allow_null=False,
        )

        def validate_roles(self, roles):
            if not roles:
                raise serializers.ValidationError(_("Empty Value Not Accepted!"))
            return roles

    def post(self, request):
        self.serializer_class = self.InputSerializer(data=request.data)
        self.serializer_class.is_valid(raise_exception=True)

        email = self.serializer_class.validated_data.pop("email")
        roles = None
        if self.serializer_class.validated_data.get("roles"):
            roles = self.serializer_class.validated_data.pop("roles")

        if roles:
            self.serializer_class.validated_data.update(
                primary_email=email,
                groups=roles,
            )
        else:
            self.serializer_class.validated_data.update(primary_email=email)

        user = User.objects.filter(
            Q(primary_email=email)
            | Q(username=self.serializer_class.validated_data.get("username"))
        ).first()
        if user and user.is_active is False:
            user.is_active = True
            user.username = self.serializer_class.validated_data.get("username")
            user.primary_email = self.serializer_class.validated_data.get(
                "primary_email"
            )
            user.contact_number = self.serializer_class.validated_data.get(
                "contact_number"
            )
            user.password = self.serializer_class.validated_data.get("password")
            user.groups = self.serializer_class.validated_data.get("roles")
            user.save()
            return Response(
                {"message": "User account created successfully!"},
                status=status.HTTP_201_CREATED,
            )

        user = create_user(**self.serializer_class.validated_data)
        if user.id:
            return Response(
                {"message": "User account created successfully!"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "User account not created."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Logout(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def get(self, request: Request):
        access_token = request.auth.decode()
        obj = AccessToken.objects.get(token=UUID(hex=access_token))
        obj.validity = AccessToken.TokenValidity.INVALID
        obj.save()
        return Response({"message": "User logged out successfully"})


class Refresh(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def get(self, request: Request):
        access_token = request.auth.decode()
        obj = AccessToken.objects.get(token=UUID(hex=access_token))
        obj.validity = AccessToken.TokenValidity.INVALID
        obj.save()

        access_token = create_token(request.user)
        return Response({"access_token": access_token})
