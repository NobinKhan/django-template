import os
import pandas as pd

from django.db.models import Q
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from apps.api.pagination import (
    LimitOffsetPagination,
    get_paginated_response,
)

from apps.users.models import User
from apps.emails.models import Email
from apps.common.exceptions import ApplicationError
from apps.product.models import Product, UploadProduct
from apps.common.detect import validate_csv_xl, validate_barcode
from apps.product.selectors import product_list, upload_product_list
from apps.product.services import create_product, create_sub_digit, create_upload_product
from apps.common.permissions import (
    AddSubNumber, AddUploadProduct, AdminUser, 
    DeleteUploadProduct, ViewUploadProduct, 
    ChangeUploadProduct, ViewProduct,
    AddProduct, 
)



# *** start ***

class CreateSubNumber(APIView):
    permission_classes = [AddSubNumber]
    serializer_class = None


    class InputSerializer(serializers.Serializer):
        number = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)

        if serializer.is_valid():
            sub_number = create_sub_digit(**serializer.validated_data)
            return Response({"message": "Sub Number Created Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateUploadProduct(APIView):
    permission_classes = [AddUploadProduct, DeleteUploadProduct]
    serializer_class = None


    class InputSerializer(serializers.Serializer):
        inventory_number = serializers.CharField(max_length=100, allow_blank=True, allow_null=True, required=False)
        asset = serializers.IntegerField(max_value=99999999999999, min_value=100000000000, required=True)
        sub_number = serializers.IntegerField(max_value=9999, min_value=0, required=True)
        cost_center = serializers.CharField(max_length=15, required=True)
        name = serializers.CharField(max_length=200, required=True)
        created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
        department = serializers.CharField(max_length=20, required=True)
        
        def create(self, validated_data):
            validated_data['created_by'] = self.context['request'].user
            product = create_upload_product(**validated_data)
            return product


    class FileInputSerializer(serializers.Serializer):
        csv_file = serializers.FileField(required=True, validators=[validate_csv_xl])
        list_data = None

        def validate_csv_file(self, value):
            # Check if file is uploaded
            if not value:
                raise ValidationError(_("File not uploaded"))

            ext = os.path.splitext(value.name)[1]
            if ext.lower() == '.csv':
                # Try to read file as CSV
                try:
                    df = pd.read_csv(value)
                    df.columns = [name.lower().replace(' ', '_').replace('-', '_').replace('_(printed_on_rfid_tag)', '') for name in df.columns]  # change column names
                    df.fillna('', inplace=True)
                    self.list_data = df.to_dict('records') 
                except:
                    print("CSV File Error")

            elif ext.lower() == '.xlsx':
                # Try to read file as XLSX
                try:
                    df = pd.read_excel(value)
                    df.columns = [name.lower().replace(' ', '_').replace('-', '_').replace('_(printed_on_rfid_tag)', '') for name in df.columns]  # change column names
                    df.fillna('', inplace=True)
                    self.list_data = df.to_dict('records') 
                except:
                    print("xl File Error")
            else:
                raise ValidationError(_("File Encoding May Not Valid!"))
            return value


    def post(self, request):
        content_type = request.content_type

        # Product create by uploading file
        if 'multipart/form-data' in content_type:
            file_serializer = self.FileInputSerializer(data=request.data)
            if file_serializer.is_valid():

                serializer = self.InputSerializer(data=file_serializer.list_data, many=True, context={'request': request})
                try:
                    if serializer.is_valid():
                        delete = UploadProduct.objects.all().delete()
                        serializer.save()
                        return Response({"message": "Products Created Successfully"}, status=status.HTTP_201_CREATED)
                except IntegrityError:
                    return Response({"message": "Duplicate Value Detected!"}, status=status.HTTP_403_FORBIDDEN)
                errors = serializer.errors
                if isinstance(errors, list):
                    return Response([d for d in errors if d], status=status.HTTP_403_FORBIDDEN)
                return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
            return Response(file_serializer.errors, status=status.HTTP_403_FORBIDDEN)
            
        
        # Manual product creation
        if content_type == 'application/json':
            print(request.data)
            if isinstance(request.data, dict):
                
                serializer = self.InputSerializer(data=request.data, context={'request': request})
                try:
                    if serializer.is_valid():
                        serializer.save()
                        return Response({"message": "Created Successfully"}, status=status.HTTP_201_CREATED)
                except IntegrityError:
                    return Response({"message": "Duplicate Value Detected!"}, status=status.HTTP_403_FORBIDDEN)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if isinstance(request.data, list):
                serializer = self.InputSerializer(data=request.data, many=True, context={'request': request})

                if serializer.is_valid():
                    try:
                        delete = UploadProduct.objects.all().delete()
                        serializer.save()
                        return Response({"message": "Created Successfully"}, status=status.HTTP_201_CREATED)
                    except IntegrityError as msg:
                        return Response({"message": msg.args}, status=status.HTTP_403_FORBIDDEN)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Invalid Json Format"}, status=status.HTTP_403_FORBIDDEN)


class UploadProductList(APIView):

    permission_classes = [ViewUploadProduct]
    serializer_class = None


    class Pagination(LimitOffsetPagination):
        default_limit = 20
        max_limit = None

    class OutputSerializer(serializers.ModelSerializer):
        created_by = serializers.SerializerMethodField(read_only=True)
        cost_center = serializers.SerializerMethodField(read_only=True)
        asset = serializers.SerializerMethodField(read_only=True)
        department = serializers.SerializerMethodField(read_only=True)
        
        class Meta:
            model = UploadProduct
            fields = ("id", "asset", "sub_number", "created_by", "name", "created_at", "inventory_number", "cost_center","department",)

        def get_created_by(self, attb):
            if attb.created_by:
                return attb.created_by.username
            return "No User Found"

        def get_cost_center(self, attb):
            if attb.cost_center== None:
                return None
            return attb.cost_center.name

        def get_asset(self, attb):
            return attb.asset.number

        def get_department(self, attb):
            if attb.department:
                return attb.department.name
            else:
                return "no_data"

    def get(self, request):
        prducts = upload_product_list()

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=prducts,
            request=request,
            view=self,
        )


class UpdateUploadProduct(APIView):

    permission_classes = [ChangeUploadProduct]
    serializer_class = None


    class Pagination(LimitOffsetPagination):
        default_limit = 20

    class OutputSerializer(serializers.ModelSerializer):
        created_by = serializers.SerializerMethodField(read_only=True)
        cost_center = serializers.SerializerMethodField(read_only=True)
        asset = serializers.SerializerMethodField(read_only=True)
        department = serializers.SerializerMethodField(read_only=True)

        class Meta:
            model = UploadProduct
            fields = ("id", "asset", "sub_number", "created_by", "name", "created_at", "inventory_number", "cost_center", "department")

        def get_created_by(self, attb):
            return attb.created_by.username

        def get_cost_center(self, attb):
            return attb.cost_center.name

        def get_asset(self, attb):
            return attb.asset.number

        def get_department(self, attb):
            return attb.department.name

    def get(self, request):
        prducts = upload_product_list()

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=prducts,
            request=request,
            view=self,
        )


class ProductList(APIView):

    permission_classes = [ViewProduct]
    serializer_class = None


    class Pagination(LimitOffsetPagination):
        default_limit = 20
        max_limit = None

    class OutputSerializerWeb(serializers.ModelSerializer):
        created_by = serializers.SerializerMethodField(read_only=True)
        cost_center = serializers.SerializerMethodField(read_only=True)
        asset = serializers.SerializerMethodField(read_only=True)
        send_by = serializers.SerializerMethodField(read_only=True)
        inventory_number = serializers.SerializerMethodField(read_only=True)
        department = serializers.SerializerMethodField(read_only=True)
        tag_type = serializers.SerializerMethodField(read_only=True)

        class Meta:
            model = Product
            fields = ("id", "asset", "sub_number", "created_by", "name", "created_at", "inventory_number", 'tag_type', "cost_center", "send_by", "email_sent_status", "department")

        def get_tag_type(self, attb):
            if attb.tag:
                return attb.tag.tag_type
            else:
                return "Barcode"

        def get_created_by(self, attb):
            if attb.created_by:
                return attb.created_by.username
            return "No User Found"

        def get_send_by(self, attb):
            if attb.send_by is not None:
                return attb.send_by.username
            return None

        def get_cost_center(self, attb):
            return attb.cost_center.name

        def get_asset(self, attb):
            return attb.asset.number

        def get_department(self, attb):
            if attb.department:
                return attb.department.name
            else:
                return "no_data"
        
        def get_inventory_number(self, attb):
            if not attb.inventory_number:
                return f"{attb.asset}-{attb.sub_number}"
            return attb.inventory_number


    class OutputSerializerApp(serializers.ModelSerializer):
        cost_center = serializers.SerializerMethodField(read_only=True)
        asset = serializers.SerializerMethodField(read_only=True)
        department = serializers.SerializerMethodField(read_only=True)
        tag_type = serializers.SerializerMethodField(read_only=True)

        class Meta:
            model = Product
            fields = ("asset", "sub_number", "inventory_number", 'tag_type', "cost_center", "department", "name")

        def get_tag_type(self, attb):
            if attb.tag:
                return attb.tag.tag_type
            else:
                return "Barcode"

        def get_cost_center(self, attb):
            return attb.cost_center.name

        def get_asset(self, attb):
            return attb.asset.number

        def get_department(self, attb):
            if attb.department:
                return attb.department.name
            else:
                return "not_found"

    def get(self, request):
        client = request.query_params.get('client')
        if not client or client not in ['app', 'web']:
            return Response({"message": "Invalid request"}, status=status.HTTP_403_FORBIDDEN)

        prducts = None
        if client == 'app':
            prducts = product_list(filters={
                "send_by": request.user, 
                "email_sent_status": Product.SendStatus.SEND
            })
            return get_paginated_response(
                pagination_class=self.Pagination,
                serializer_class=self.OutputSerializerApp,
                queryset=prducts,
                request=request,
                view=self,
            )

        if client == 'web':
            prducts = product_list()

            return get_paginated_response(
                pagination_class=self.Pagination,
                serializer_class=self.OutputSerializerWeb,
                queryset=prducts,
                request=request,
                view=self,
            )


class DeleteProduct(APIView):
    permission_classes = [DeleteUploadProduct]
    serializer_class = None


    class InputSerializer(serializers.Serializer):
        ids = serializers.ListField(child=serializers.IntegerField(), required=True)


    def delete(self, request, pk=None):
        # Single item delete
        if pk:
            try:
                instance = UploadProduct.objects.get(pk=pk)
            except UploadProduct.DoesNotExist:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
            instance.delete()
            return Response({"message": "Deleted"},status=status.HTTP_200_OK)

        # Multiple items delete
        else:
            serializer = self.InputSerializer(data=request.data)
            if serializer.is_valid():
                id_list = serializer.validated_data['ids']
                queryset = UploadProduct.objects.filter(pk__in=id_list)
                if not queryset.exists():
                    return Response({"error": "No objects found with the provided ids."}, status=status.HTTP_404_NOT_FOUND)
                queryset.delete()
                return Response({"message": "Deleted"},status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteScannedProduct(APIView):
    permission_classes = [DeleteUploadProduct]
    serializer_class = None


    class InputSerializer(serializers.Serializer):
        ids = serializers.ListField(child=serializers.IntegerField(allow_null=True), required=True)

    def delete(self, request, pk=None):
        # Single item delete
        if pk:
            try:
                instance = Product.objects.get(pk=pk)
            except Product.DoesNotExist:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
            instance.delete()
            return Response({"message": "Deleted"},status=status.HTTP_200_OK)
        
        # Multiple items delete
        else:
            serializer = self.InputSerializer(data=request.data)
            if serializer.is_valid():
                id_list = serializer.validated_data['ids']
                queryset = Product.objects.filter(pk__in=id_list)
                if not queryset.exists():
                    return Response({"error": "No objects found with the provided ids."}, status=status.HTTP_404_NOT_FOUND)
                queryset.delete()
                return Response({"message": "Deleted"},status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScanProduct(APIView):

    permission_classes = [ViewUploadProduct, AddProduct]
    serializer_class = None


    class InputSerializer(serializers.Serializer):
        inventory_number = serializers.CharField(required=True)
        invalid_data = None

        def validate_inventory_number(self, value):
                # Check if data empty or null
                if not value:
                    raise serializers.ValidationError(_("Empty or Null data may not acceptable"))

                # Get the product object from Permanent Product table
                if len(value.split('-')[0]) == 5 and value.startswith('D'):
                    value = value.replace('D', '', 1)
                tag = validate_barcode(code_str=value)
                if tag is None:
                    self.invalid_data = {
                        "asset": "Not_PUB_asset",
                        "sub_number": "Not_PUB_asset",
                        "inventory_number": value,
                        "cost_center": "Not_PUB_asset",
                        "name": "Not_PUB_asset",
                        "department": "Not_PUB_asset",
                    }
                    raise ApplicationError(_("invalid_inventory_number"))

                elif tag == 'BARCODE':
                    asset, sub_number = value.split('-')
                    instance = Product.objects.filter(asset__number=asset, sub_digit__number=sub_number)

                elif tag == 'RFID':
                    instance = Product.objects.filter(tag__tag=value)

                if instance:
                    if instance[0].email_sent_status in [Product.SendStatus.SEND, Product.SendStatus.SEND_USER_DELETED]:
                        self.invalid_data = {
                            "asset": "already_sent",
                            "sub_number": "already_sent",
                            "inventory_number": value,
                            "cost_center": "already_sent",
                            "name": "already_sent",
                            "department": "already_sent",
                        }
                        raise ApplicationError(_("already_sent"))
                    else:
                        self.invalid_data = {
                            "asset": "already_scanned",
                            "sub_number": "already_scanned",
                            "inventory_number": value,
                            "cost_center": "already_scanned",
                            "name": "already_scanned",
                            "department": "already_scanned",
                        }
                        raise ApplicationError(_("already_scanned"))

                # Get the product object from temporary Product table
                if tag == 'BARCODE':
                    asset, sub_number = value.split('-')
                    instance = UploadProduct.objects.filter(asset__number=asset, sub_digit__number=sub_number)

                elif tag == 'RFID':
                    instance = UploadProduct.objects.filter(tag__tag=value)

                if not instance:
                    # raise serializers.ValidationError(f"Product with inventory number {value} does not exist.")
                    self.invalid_data = {
                        "asset": "No_longer_in_asset_list",
                        "sub_number": "No_longer_in_asset_list",
                        "inventory_number": value,
                        "cost_center": "No_longer_in_asset_list",
                        "name": "No_longer_in_asset_list",
                        "department": "No_longer_in_asset_list",
                    }
                    raise ApplicationError(message=_("not_exists"))

                return instance

        def create(self, validated_data):
            # save product to permanent table
            products = []
            for product in validated_data.get('inventory_number'):
                obj = create_product(
                    asset=product.asset.number,
                    sub_number=product.sub_number,
                    tag=product.tag,
                    cost_center=product.cost_center.name,
                    department=product.department.name if product.department else None,
                    name=product.name,
                    created_by=product.created_by,
                    send_by=self.context.get('request').user,
                )
                products.append(obj)
            return products


    class OutputSerializer(serializers.ModelSerializer):
        created_by = serializers.SerializerMethodField(read_only=True)
        cost_center = serializers.SerializerMethodField(read_only=True)
        asset = serializers.SerializerMethodField(read_only=True)
        id = serializers.SerializerMethodField(read_only=True)
        sub_number = serializers.SerializerMethodField(read_only=True)
        name = serializers.SerializerMethodField(read_only=True)
        created_at = serializers.SerializerMethodField(read_only=True)
        inventory_number = serializers.SerializerMethodField(read_only=True)
        tag_type = serializers.SerializerMethodField(read_only=True)
        department = serializers.SerializerMethodField(read_only=True)

        class Meta:
            model = Product
            fields = ("id", "asset", "sub_number", "created_by", "name", "created_at", "inventory_number", 'tag_type', "cost_center", 'department')

        def get_created_by(self, attb):
            return attb[0].created_by.username

        def get_cost_center(self, attb):
            return attb[0].cost_center.name

        def get_department(self, attb):
            return attb[0].department.name if attb[0].department else "NoDepartment"

        def get_asset(self, attb):
            return attb[0].asset.number

        def get_id(self, attb):
            return attb[0].id

        def get_sub_number(self, attb):
            return attb[0].sub_number

        def get_name(self, attb):
            return attb[0].name

        def get_created_at(self, attb):
            return attb[0].created_at

        def get_inventory_number(self, attb):
            return attb[0].inventory_number
        
        def get_tag_type(self, attb):
            if attb[0].tag:
                return attb[0].tag.tag_type
            else:
                return "Barcode"


    def post(self, request):

        print(f"\n\nscan api running\n")
        print(f"body data")
        print(request.data)

        if isinstance(request.data, list):
            data: dict = request.data
            unique = [{"inventory_number": x.replace('*', '').replace('\x00', '')} for x in set(item for sublist in data for item in sublist) if x is not None and x != ""]
            print(f"Uniqe_data = {unique}")
            count = 1
            response = []
            in_serializer = None
            for every in unique:
                try:
                    in_serializer = self.InputSerializer(data=every, context={"request": request})
                    if in_serializer.is_valid():
                        in_serializer.save()
                        out_serializer = self.OutputSerializer(in_serializer.instance)
                        response.append(out_serializer.data)
                        print(f"index-{count} successfully posted")
                except ApplicationError as msg:
                    print(f"index-{count} error occured")
                    print(msg.message)
                    response.append(in_serializer.invalid_data)
                count+=1
            if response:
                return Response(response)
            elif in_serializer:
                try:
                    return Response(in_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except AssertionError:
                    return Response({
                        "asset": "Not_PUB_asset",
                        "sub_number": "Not_PUB_asset",
                        "inventory_number": in_serializer.initial_data.get('inventory_number'),
                        "cost_center": "Not_PUB_asset",
                        "name": "Not_PUB_asset",
                        "department": "Not_PUB_asset",
                    })
            else:
                return Response({"error": "empty data may not be allowed"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Invalid body data!"}, status=status.HTTP_406_NOT_ACCEPTABLE)


class GetScannedProduct(APIView):

    permission_classes = [ViewProduct]
    serializer_class = None


    class OutputSerializer(serializers.ModelSerializer):
        created_by = serializers.SerializerMethodField(read_only=True)
        cost_center = serializers.SerializerMethodField(read_only=True)
        asset = serializers.SerializerMethodField(read_only=True)
        department = serializers.SerializerMethodField(read_only=True)
        tag_type = serializers.SerializerMethodField(read_only=True)

        class Meta:
            model = Product
            fields = ("id", "asset", "sub_number", "created_by", "name", "created_at", "inventory_number", 'tag_type', "cost_center", "department")

        def get_created_by(self, attb):
            return attb.created_by.username

        def get_cost_center(self, attb):
            return attb.cost_center.name

        def get_asset(self, attb):
            return attb.asset.number

        def get_department(self, attb):
            if attb.department:
                return attb.department.name
            else:
                return "NoDepartment"
        
        def get_tag_type(self, attb):
            if attb.tag:
                return attb.tag.tag_type
            else:
                return "Barcode"


    def get(self, request):
        prducts = Product.objects.filter(send_by=request.user, email_sent_status=Product.SendStatus.NOT_SEND).order_by('asset__number')
        serializer = self.OutputSerializer(prducts, many=True)
        return Response(serializer.data)



class DashBoardDeatilsApi(APIView):

    permission_classes = [AdminUser]
    serializer_class = None

    def get(self, request):

        totaluser = User.objects.filter(is_superuser=0).count()
        totalproduct = UploadProduct.objects.all().count()
        emailsdata= Email.objects.all().exclude(Q(email__icontains='@care-box.com') |  Q(role='carebox')).count()
        user = User.objects.all().values('username').exclude(is_superuser=True)

        list = []
        DATA = []

        for users in user:
            userid = User.objects.filter(username=users['username']).exclude(is_superuser=True)
            list.append(users['username'])
            count= Product.objects.filter(send_by__username=users['username']).count()
            DATA.append(count)

        my_dict = dict(zip(list,DATA))
        username = list
        scan = DATA
        length = len(list)
        list1 =[]

        for i in range(0,length):
            dict1 = {
                "username": list[i],
                "scan_data": DATA[i],
                
            }
            list1.append(dict1)

        return Response([{"totaluser":totaluser},{"totalproduct":totalproduct},{"email":emailsdata},list1])

# *** End ***
