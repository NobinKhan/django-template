from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.pagination import LimitOffsetPagination, get_paginated_response
from apps.cost_center.models import CostCenter
from apps.cost_center.services import create_cost_center


class CreateCostCenter(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)

    def post(self, request):
        self.serializer_class = self.InputSerializer(data=request.data)

        if self.serializer_class.is_valid():
            create_cost_center(**self.serializer_class.validated_data)
            return Response(
                {"message": "New Cost-Center-ID Created Successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            self.serializer_class.errors, status=status.HTTP_400_BAD_REQUEST
        )


class CostCenterListApi(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = CostCenter
            fields = ("id", "name", "is_active", "created_at")

    def get(self, request):
        cost_center = CostCenter.objects.all()
        self.serializer_class = self.OutputSerializer

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=cost_center,
            request=request,
            view=self,
        )
