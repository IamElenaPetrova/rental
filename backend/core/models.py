from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at',
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_%(class)ss',
        verbose_name='Created by',
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='updated_%(class)ss',
        verbose_name='Updated by',
    )

    class Meta:
        abstract = True
        ordering = ('-created_at',)
