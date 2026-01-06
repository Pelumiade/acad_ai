from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """Mixin that adds created_at and updated_at timestamp fields."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
