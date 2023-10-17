import os

import pytz
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.emails.models import Email
from apps.product.models import Product


class SendEmail(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    class InputSerializer(serializers.Serializer):
        ids = serializers.ListField(
            child=serializers.PrimaryKeyRelatedField(
                queryset=Product.objects.all(), allow_null=True
            ),
            allow_empty=False,
        )

    def post(self, request):
        data = [item for item in request.data.get("ids") if item is not None]
        request.data.update({"ids": data})
        self.serializer_class = self.InputSerializer(data=request.data)

        if self.serializer_class.is_valid():
            emails = [obj.email for obj in Email.objects.all()]
            if emails is None:
                return Response(
                    {"message": "Please set some emails!"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Set the timezone to Singapore
            sg_timezone = pytz.timezone("Asia/Singapore")

            # Get the current time in Singapore
            sg_time = timezone.now().astimezone(sg_timezone)

            # first file
            file1 = open(
                f"{request.user.username}-{timezone.now().microsecond}.txt",
                "w",
                newline="",
            )

            # second file
            file2 = open(
                f"{request.user.username}-{timezone.now().microsecond}-RFID.txt",
                "w",
                newline="",
            )
            flag = None

            for product in self.serializer_class.validated_data.get("ids"):
                file1.write(
                    "   {}          {}   {}{}".format(
                        f"{product.asset.number}{product.sub_number}{product.created_at.strftime('%Y%m%d')}",
                        request.user.username,
                        sg_time.strftime("%H%M%S"),
                        "\n",
                    )
                )
                if product.is_rfid:
                    flag = True
                    file2.write(
                        "   {}          {}   {}   {}{}".format(
                            f"{product.asset.number}{product.sub_number}{product.created_at.strftime('%Y%m%d')}",
                            request.user.username,
                            sg_time.strftime("%H%M%S"),
                            product.inventory_number,
                            "\n",
                        )
                    )

            file1.close()
            file2.close()

            subject, from_email = (
                f"Scanned Data From Asset Verification System (user: {request.user.username})",
                settings.EMAIL_HOST_USER,
            )
            text_content = "Scanned Data"
            html_content = f"Hi,\n<p>This is a <strong>Scanned Data</strong> message sent by user: {request.user.username}</p>"
            msg = EmailMultiAlternatives(subject, text_content, from_email, emails)
            msg.attach_alternative(html_content, "text/html")
            msg.attach_file(file1.name, "text/file")
            if flag:
                msg.attach_file(file2.name, "text/file")
            msg.send()
            os.remove(path=file1.name)
            os.remove(path=file2.name)

            # Product status update
            for product in self.serializer_class.validated_data.get("ids"):
                product.email_sent_status = Product.SendStatus.SEND
                product.send_by = request.user
                product.save()
            return Response(
                {"message": "Email sending!"}, status=status.HTTP_201_CREATED
            )
        return Response(
            self.serializer_class.errors, status=status.HTTP_400_BAD_REQUEST
        )
