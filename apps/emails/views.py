from apps.common.permissions import AddEmail, ChangeEmail, DeleteEmail, ViewEmail
from django.db.models import Q
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.emails.models import Email
from apps.emails.serializers import Emailserializer


class EmailCreateView(APIView):
    permission_classes = [AddEmail]
    serializer_class = None

    def post(self, request):
        self.serializer_class = Emailserializer(data=request.data, many=False)
        if self.serializer_class.is_valid():
            self.serializer_class.save()
            return Response(self.serializer_class.data, status=status.HTTP_201_CREATED)
        return Response(
            self.serializer_class.errors, status=status.HTTP_400_BAD_REQUEST
        )


class EmailListView(APIView):
    permission_classes = [ViewEmail]
    serializer_class = None

    def get(self, request):
        data = Email.objects.all().exclude(
            Q(email__icontains="@care-box.com") | Q(role="carebox")
        )
        self.serializer_class = Emailserializer(data, many=True)

        if self.serializer_class.data == []:
            return Response(
                {"message": "data not found"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(self.serializer_class.data, status=status.HTTP_200_OK)


class EmailDeleteView(APIView):
    permission_classes = [ChangeEmail, DeleteEmail]
    serializer_class = None

    def get_object(self, pk):
        try:
            return Email.objects.get(email=pk)
        except Email.DoesNotExist:
            raise Http404

    def delete(self, request, pk, format=None):
        data = self.get_object(pk)
        data.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_200_OK
        )

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        self.serializer_class = Emailserializer(snippet, data=request.data)
        if self.serializer_class.is_valid():
            self.serializer_class.save()
            return Response(self.serializer_class.data)
        return Response(
            self.serializer_class.errors, status=status.HTTP_400_BAD_REQUEST
        )
