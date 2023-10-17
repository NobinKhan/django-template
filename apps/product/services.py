from apps.common.detect import validate_barcode
from apps.common.services import model_update
from apps.common.utils import get_object
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _

from apps.cost_center.models import CostCenter
from apps.cost_center.services import create_cost_center
from apps.product.models import (
    Asset,
    Department,
    Product,
    SubNumber,
    Tag,
    UploadProduct,
)
from apps.users.models import User


def create_asset(*, number: int = None) -> Asset:
    if not number:
        raise ValidationError(_("Empty Data Not Allowed"))

    # object creation
    asset = Asset.objects.get_or_create(number=number)
    return asset


def create_sub_digit(*, number: int = None) -> SubNumber:
    # object creation
    sub_number = SubNumber.objects.get_or_create(number=number)
    return sub_number


def create_department(*, name: int = None) -> Department:
    if not name:
        raise ValidationError(_("Empty Data Not Allowed"))

    # object creation
    department = Department.objects.get_or_create(name=name)
    return department


def create_inventory_number(*, tag: str = None) -> Tag:
    # object creation
    obj = None
    if tag:
        obj = get_object(Tag, tag=tag)
        if not obj:
            obj = Tag.objects.create(tag=tag)
            obj.full_clean()
            obj.save()
    return obj


def create_product_admin(
    *,
    tag: str = None,
    asset: Asset = None,
    sub_digit: SubNumber = None,
    cost_center: CostCenter = None,
    name: str = None,
    created_by: User = None,
    **kwrgs,
) -> Product:
    if not asset or not cost_center or not name or not created_by or not sub_digit:
        raise ValidationError(_("Empty Data Not Allowed"))

    tag_type = None
    if tag:
        tag = validate_barcode(code_str=tag)
        if not tag:
            raise ValidationError(_("Invalid RFID Tag!"))
        elif tag == "RFID":
            tag_type = Product.TagType.RFID
        elif tag == "BARCODE":
            tag_type = Product.TagType.BARCODE
            tag = None
    else:
        tag_type = Product.TagType.BARCODE

    try:
        product = Product.objects.create(
            asset=asset,
            tag=tag,
            tag_type=tag_type,
            sub_digit=sub_digit,
            cost_center=cost_center,
            created_by=created_by,
            name=name,
        )
    except IntegrityError as error_msg:
        raise ValidationError(_(error_msg.args[0].splitlines()[1]))

    product.full_clean()
    product.save()
    return product


def create_upload_product(
    *,
    inventory_number: str = None,
    asset: int = None,
    sub_number: int = None,
    cost_center: str = None,
    name: str = None,
    created_by=None,
    department: str = None,
) -> UploadProduct:
    if not asset or not cost_center or not created_by:
        raise ValidationError(_("Empty Data Not Allowed"))

    asset = create_asset(number=asset)[0]
    sub_digit = create_sub_digit(number=sub_number)[0]
    cost_center = create_cost_center(name=cost_center)[0]
    department = create_department(name=department)[0]
    tag = create_inventory_number(tag=inventory_number)

    upload_product = UploadProduct.objects.create(
        asset=asset,
        tag=tag,
        sub_digit=sub_digit,
        cost_center=cost_center,
        created_by=created_by,
        name=name,
        department=department,
    )

    upload_product.full_clean()
    upload_product.save()

    return upload_product


def create_product(
    *,
    tag: Tag = None,
    asset: Asset = None,
    sub_number: SubNumber = None,
    department: Department = None,
    cost_center: CostCenter = None,
    name: str = None,
    created_by: User = None,
    send_by: User = None,
) -> Product:
    if not asset or not cost_center or not created_by or not send_by or not Department:
        raise ValidationError(_("Empty Data Not Allowed"))

    asset = create_asset(number=asset)[0]
    sub_digit = create_sub_digit(number=sub_number)[0]
    cost_center = create_cost_center(name=cost_center)[0]
    department = create_department(name=department)[0]

    try:
        product = Product.objects.create(
            asset=asset,
            tag=tag,
            sub_digit=sub_digit,
            cost_center=cost_center,
            created_by=created_by,
            name=name,
            send_by=send_by,
            department=department,
        )
    except IntegrityError as error_msg:
        raise ValidationError(_(error_msg.args[0].splitlines()[1]))

    product.full_clean()
    product.save()
    return product


@transaction.atomic
def upload_product_update(*, product: UploadProduct, data) -> UploadProduct:
    non_side_effect_fields = [
        "asset",
        "sub_digit",
        "cost_center",
        "contact_number",
        "groups",
        "department",
    ]

    product, has_updated = model_update(
        instance=product, fields=non_side_effect_fields, data=data
    )

    return product, has_updated
