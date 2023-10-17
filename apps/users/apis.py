from apps.common.permissions import ChangeUser, DeleteUser, ViewRole, ViewUser
from apps.common.utils import get_object
from django.contrib.auth.models import Group
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import request, serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.pagination import LimitOffsetPagination, get_paginated_response
from apps.users.models import User
from apps.users.selectors import user_list
from apps.users.services import user_update


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("style", {})
        kwargs["style"]["input_type"] = "password"
        kwargs["write_only"] = True
        super().__init__(*args, **kwargs)


class UpdateUser(APIView):
    permission_classes = [ChangeUser]
    serializer_class = None

    class InputSerializer(serializers.Serializer):
        username = serializers.CharField(
            required=False, allow_blank=False, allow_null=False
        )
        email = serializers.EmailField(
            required=False, allow_blank=False, allow_null=False
        )
        contact_number = PhoneNumberField(
            required=False, allow_blank=False, allow_null=False
        )
        password = PasswordField(required=False, allow_blank=False, allow_null=False)
        roles = serializers.ListField(
            child=serializers.CharField(allow_blank=False, allow_null=False),
            required=False,
            allow_null=False,
        )

        def validate_roles(self, roles):
            if not roles:
                raise serializers.ValidationError(_("Empty Value Not Accepted!"))
            return roles

    def post(self, request, pk):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        roles = None
        email = None
        if serializer.validated_data.get("email"):
            email = serializer.validated_data.pop("email")
        if serializer.validated_data.get("roles"):
            roles = serializer.validated_data.pop("roles")

        if roles is not None:
            serializer.validated_data.update(
                groups=roles,
            )

        if email is not None:
            serializer.validated_data.update(primary_email=email)

        user = get_object(User, pk=pk)
        updated_user, has_updated = user_update(
            user=user, data=serializer.validated_data
        )

        if has_updated:
            return Response({"message": "User account changed successfully!"})
        else:
            return Response(
                {"message": "User account not update."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserListApi(APIView):
    permission_classes = [ViewUser]
    serializer_class = None

    class Pagination(LimitOffsetPagination):
        default_limit = 1
        max_limit = None

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        is_staff = serializers.BooleanField(
            required=False, allow_null=True, default=None
        )
        email = serializers.EmailField(required=False)

    class OutputSerializer(serializers.ModelSerializer):
        roles = serializers.SerializerMethodField(read_only=True)
        email = serializers.SerializerMethodField(read_only=True)

        class Meta:
            model = User
            fields = (
                "id",
                "username",
                "contact_number",
                "email",
                "created_at",
                "roles",
            )

        def get_roles(self, obj):
            return [group.name for group in obj.groups.all()]

        def get_email(self, obj):
            return obj.primary_email

    def get(self, request):
        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        users = user_list(filters=filters_serializer.validated_data)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=users,
            request=request,
            view=self,
        )


class RoleList(APIView):
    permission_classes = [ViewRole]
    serializer_class = None

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Group
            fields = ("name",)

    def get(self, request):
        groups = Group.objects.all()
        serializer = self.OutputSerializer(groups, many=True)

        return Response(data=serializer.data)


class UserDeleteView(APIView):
    permission_classes = [DeleteUser]
    serializer_class = None

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        data = self.get_object(pk)
        data.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_200_OK
        )


class SelfDelete(GenericAPIView, DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = None

    def delete(self, request: request.Request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active is False:
            return Response(
                {"error": "user not found"}, status=status.HTTP_404_NOT_FOUND
            )
        elif request.user.id != instance.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        # Instead of deleting, set the "is_active" field to False
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Me(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def get(self, request):
        return Response({"username": request.user.username, "id": request.user.id})
