import os
from re import match

import barcode
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


def validate_barcode(code_str: str):
    barcode_pattern = r"^\d{12}-\d{1,4}$"
    rfid_pattern = r"^[A-Z\d]{4}-\d{10}$"

    try:
        barcode.get_barcode_class("ean13")(code_str)
        if match(barcode_pattern, code_str) and not match(rfid_pattern, code_str):
            return "BARCODE"
    except barcode.errors.BarcodeError:
        if match(rfid_pattern, code_str) and not match(barcode_pattern, code_str):
            return "RFID"
    return None


def validate_csv_xl(value):
    ext = os.path.splitext(value.name)[1]
    if ext.lower() not in [".csv", ".xlsx"]:
        raise ValidationError(_("File format not supported"))
