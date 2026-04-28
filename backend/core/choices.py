from django.db import models


class Currency(models.TextChoices):
    USD = 'USD', 'USD'
    PESO = 'PESO', 'PESO'
