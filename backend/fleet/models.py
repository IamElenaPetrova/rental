from django.contrib.auth import get_user_model
from django.db import models

from core.models import BaseModel

User = get_user_model()


class Car(BaseModel):
    name = models.CharField(
        max_length=255,
        verbose_name='Name',
    )
    plate_number = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='License plate',
    )
    owners = models.ManyToManyField(
        User,
        related_name='cars',
        verbose_name='Owners',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
    )

    class Meta:
        verbose_name = 'Car'
        verbose_name_plural = 'Cars'

    def __str__(self) -> str:
        return f'{self.name}'


class InsuranceCompany(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Name',
        unique=True,
    )

    class Meta:
        verbose_name = 'Insurance company'
        verbose_name_plural = 'Insurance companies'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class CarInsurance(models.Model):
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='insurances',
        verbose_name='Car',
    )
    insurer = models.ForeignKey(
        InsuranceCompany,
        on_delete=models.PROTECT,
        related_name='car_insurances',
        verbose_name='Insurance company',
    )
    policy_number = models.CharField(
        max_length=64,
        verbose_name='Policy number',
    )
    start_date = models.DateField(
        verbose_name='Start date',
    )
    end_date = models.DateField(
        verbose_name='End date',
    )

    class Meta:
        verbose_name = 'Car insurance'
        verbose_name_plural = 'Car insurances'
        ordering = ['-start_date']

    def __str__(self) -> str:
        return f'{self.insurer} — {self.policy_number} ({self.car})'
