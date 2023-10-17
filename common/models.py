from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.utils import ProgrammingError


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class CustomID(models.Model):
    def generate_id():
        try:
            last_object = get_user_model().objects.order_by("-id")[0]
            if last_object.id < 1000:
                return 1000 + last_object.id
            return last_object.id + 1
        except IndexError:
            return 1000
        except ProgrammingError:
            return None

    id = models.PositiveBigIntegerField(
        unique=True,
        default=generate_id,
        editable=False,
        db_index=True,
        primary_key=True,
        validators=[MaxValueValidator(9223372036854775807), MinValueValidator(1000)],
        blank=True,
    )

    class Meta:
        abstract = True
