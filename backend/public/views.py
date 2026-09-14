from django.shortcuts import render

from public.models import SiteSettings
from public.services import (
    published_car_by_slug,
    published_cars,
    published_house_by_slug,
    published_houses,
)


def home(request):
    site_settings = SiteSettings.load()
    return render(
        request,
        'public/home.html',
        {
            'car_count': published_cars().count(),
            'house_count': published_houses().count(),
            'hero_image': site_settings.hero_image,
        },
    )


def car_list(request):
    return render(request, 'public/car_list.html', {'cars': published_cars()})


def car_detail(request, slug):
    car = published_car_by_slug(slug)
    return render(request, 'public/car_detail.html', {'car': car})


def house_list(request):
    return render(
        request,
        'public/house_list.html',
        {'houses': published_houses()},
    )


def house_detail(request, slug):
    house = published_house_by_slug(slug)
    return render(request, 'public/house_detail.html', {'house': house})
