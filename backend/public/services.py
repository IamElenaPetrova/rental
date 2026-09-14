from django.shortcuts import get_object_or_404

from fleet.models import Car
from properties.models import House


def published_cars():
    return (
        Car.objects.filter(is_active=True, is_published=True)
        .prefetch_related('photos')
        .order_by('name')
    )


def published_car_by_slug(slug: str) -> Car:
    return get_object_or_404(published_cars(), slug=slug)


def published_houses():
    return (
        House.objects.filter(is_active=True, is_published=True)
        .prefetch_related('photos')
        .order_by('name')
    )


def published_house_by_slug(slug: str) -> House:
    return get_object_or_404(published_houses(), slug=slug)
