from typing import Collection, Optional

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.common.models import BaseModel
from apps.common.detect import validate_barcode
from apps. cost_center.models import CostCenter



class Asset(BaseModel):
    number = models.PositiveBigIntegerField(
        verbose_name=_('Asset Number'), 
        validators=[MinValueValidator(100000000000), MaxValueValidator(99999999999999)],
        unique=True, 
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return f"{self.number}"


class SubNumber(BaseModel):
    number = models.PositiveSmallIntegerField(verbose_name=_('Sub Number'), unique=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.number}"


class Tag(BaseModel):
    class TagType(models.TextChoices):
        NONE = 'NONE', _('None')
        RFID = 'RFID', _('RFID')
        BARCODE = 'BARCODE', _('Barcode')
        INVALID = 'INVALID', _('Invalid')

    tag = models.CharField(verbose_name=_("Scanned Tag (Barcode/RFID) "), max_length=100, unique=True, null=True, blank=True)
    tag_type = models.CharField(default=None, max_length=10, choices=TagType.choices, blank=True, null=True)
    
    def clean_fields(self, exclude: Optional[Collection[str]] = ...) -> None:
        if self.tag:
            tag_type = validate_barcode(code_str=self.tag)
            if tag_type == self.TagType.BARCODE:
                self.tag_type = self.TagType.BARCODE
            
            if tag_type == self.TagType.RFID:
                self.tag_type = self.TagType.RFID

            if tag_type == None:
                self.tag_type = self.TagType.INVALID
        else:
            self.tag_type = self.TagType.NONE

        return super().clean_fields(exclude)

    def __str__(self):
        if not self.tag:
            return "BARCODE"
        return f"{self.tag}"


class Department(BaseModel):
    name = models.CharField(verbose_name=_('Department'), max_length=20, null=True, blank=True)

    def __str__(self):
        if not self.name:
            return "no_name"
        return f"{self.name}"


class UploadProduct(BaseModel):

    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='products', blank=True, null= True)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='products', blank=True, null= True)
    sub_digit = models.ForeignKey(SubNumber, on_delete=models.PROTECT, related_name='products', verbose_name=_("Sub-Number"), blank=True, null= True)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT, related_name='products', blank=True, null= True)
    cost_center = models.ForeignKey(CostCenter, on_delete=models.PROTECT, related_name='products', blank=True, null= True)
    name = models.CharField(verbose_name=_('Name/Description'), max_length=200, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='products', blank=True, null= True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["asset", "sub_digit"],
                name="unique_upload_product"
            )
        ]

    @property
    def sub_number(self):
    
        if self.sub_digit == None:
            return None
          
        if self.sub_digit.number == 0:
            return "0000"

        num_str = str(self.sub_digit.number)
        if len(num_str) < 4:
            num_str = "0"*(4-len(num_str)) + num_str
        return num_str

    @property
    def description(self):
        return self.name

    @property
    def tag_type(self):
        if self.tag:
            return self.tag.tag_type
        else:
            return Tag.TagType.BARCODE

    @property
    def inventory_number(self):
        if self.tag:
            if self.tag.tag_type == Tag.TagType.RFID:
                return self.tag.tag
            if self.tag.tag_type == Tag.TagType.INVALID:
                return "Invalid Tag"
        else:
            if self.asset and self.sub_number:
                return f"{self.asset.number}-{self.sub_number}"
        return "Invalid Tag"


    def __str__(self):
        return f"{self.id}"


class Product(BaseModel):

    class SendStatus(models.TextChoices):
        SEND = 'send', _('Sent By Email')
        NOT_SEND = 'not_sent', _('Not sent but scanned')
        SEND_USER_DELETED = 'sent_user_deleted', _('Sent In Email But User Deleted')

    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='send_products', blank=True, null= True)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='send_products', blank=True, null= True)
    sub_digit = models.ForeignKey(SubNumber, on_delete=models.PROTECT, related_name='send_products', verbose_name=_("Sub-Number"), blank=True, null= True)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT, related_name='send_products', blank=True, null= True)
    cost_center = models.ForeignKey(CostCenter, on_delete=models.PROTECT, related_name='send_products', blank=True, null= True)
    name = models.CharField(verbose_name=_('Name/Description'), max_length=200, blank=True, null=True)
    email_sent_status = models.CharField(default=SendStatus.NOT_SEND, max_length=20, choices=SendStatus.choices, blank=True, null=True)
    send_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='product_sends', blank=True, null= True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='product_sends', blank=True, null= True)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["asset", "sub_digit"],
                name="unique_product"
            )
        ]

    @property
    def sub_number(self):
        if self.sub_digit.number == 0:
            return "0000"

        num_str = str(self.sub_digit.number)
        if len(num_str) < 4:
            num_str = "0"*(4-len(num_str)) + num_str
        return num_str

    @property
    def description(self):
        return self.name

    @property
    def inventory_number(self):
        if self.tag:
            if self.tag.TagType.RFID == Tag.TagType.RFID:
                return self.tag.tag
            
            if self.tag.TagType.INVALID == Tag.TagType.INVALID:
                return self.tag.tag
            
            if self.tag.TagType.BARCODE == Tag.TagType.BARCODE:
                return f"{self.asset.number}-{self.sub_number}"
        else:
            if self.asset and self.sub_number:
                return f"{self.asset.number}-{self.sub_number}"
        return "Invalid Tag"

    @property
    def is_rfid(self):
        if self.tag:
            if self.tag.TagType.RFID == Tag.TagType.RFID:
                return True
        return False

    def __str__(self):
        return f"{self.id}"

    def clean_fields(self, exclude: Optional[Collection[str]] = ...) -> None:
        if self._state.adding == True:
            if not self.send_by:
                raise ValidationError(_("Must set send_by user field"))

        elif self._state.adding == False:
            old = Product.objects.get(id=self.id)

            if old.send_by and not self.send_by:
                self.email_sent_status = self.SendStatus.SEND_USER_DELETED
        return super().clean_fields(exclude)

