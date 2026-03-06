from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views.bookings import (
    BookingViewSet,
    BookingIncomeListCreateAPIView,
    BookingIncomeDetailAPIView,
)
from api.views.cars import CarViewSet
from api.views.finance import ExpenseViewSet
from api.views.renters import RenterViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'cars', CarViewSet, basename='car')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'renters', RenterViewSet, basename='renter')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'bookings/<int:booking_id>/incomes/',
        BookingIncomeListCreateAPIView.as_view(),
        name='booking-incomes',
    ),
    path(
        'bookings/<int:booking_id>/incomes/<int:pk>/',
        BookingIncomeDetailAPIView.as_view(),
        name='booking-income-detail',
    ),
]
