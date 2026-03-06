from decimal import Decimal

from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied

from bookings.models import Booking
from finance.models import Income
from api.permissions import IsCarOwnerOrAdmin
from api.serializers.bookings import (
    BookingReadSerializer,
    BookingWriteSerializer,
)
from api.serializers.finance import (
    IncomeReadSerializer,
    IncomeWriteSerializer,
)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('car', 'renter', 'created_by', 'updated_by')
    permission_classes = [permissions.IsAuthenticated, IsCarOwnerOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            qs = qs.filter(car__owners=self.request.user)
        return qs.order_by('created_at').annotate(
            total_paid=Coalesce(
                Sum('incomes__amount_in_booking_currency'),
                Value(Decimal('0'), output_field=DecimalField()),
                output_field=DecimalField(),
            )
        )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return BookingReadSerializer
        return BookingWriteSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user, updated_by=user)

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(updated_by=user)


class BookingIncomeListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_booking(self):
        booking_id = self.kwargs.get('booking_id')
        try:
            booking = Booking.objects.select_related('car').get(pk=booking_id)
        except Booking.DoesNotExist:
            raise NotFound('Бронирование не найдено.')
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            if not booking.car.owners.filter(pk=self.request.user.pk).exists():
                raise PermissionDenied(
                    'Доступ только к оплатам по бронированиям своих машин.'
                )
        return booking

    def get_queryset(self):
        booking = self.get_booking()
        return Income.objects.filter(
            booking=booking
        ).select_related(
            'booking', 'received_by'
        ).prefetch_related('photos')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return IncomeReadSerializer
        return IncomeWriteSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['booking'] = self.get_booking()
        return ctx

    def perform_create(self, serializer):
        booking = self.get_booking()
        user = self.request.user
        serializer.save(
            booking=booking,
            created_by=user,
            updated_by=user,
        )


class BookingIncomeDetailAPIView(generics.RetrieveUpdateAPIView):
    """Получение и обновление одной оплаты. Редактировать может только создатель записи."""
    permission_classes = [permissions.IsAuthenticated]

    def get_booking(self):
        booking_id = self.kwargs.get('booking_id')
        try:
            booking = Booking.objects.select_related('car').get(pk=booking_id)
        except Booking.DoesNotExist:
            raise NotFound('Бронирование не найдено.')
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            if not booking.car.owners.filter(pk=self.request.user.pk).exists():
                raise PermissionDenied(
                    'Доступ только к оплатам по бронированиям своих машин.'
                )
        return booking

    def get_queryset(self):
        booking = self.get_booking()
        return Income.objects.filter(booking=booking).select_related(
            'booking', 'received_by'
        ).prefetch_related('photos')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return IncomeReadSerializer
        return IncomeWriteSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['booking'] = self.get_booking()
        return ctx

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by_id != request.user.pk:
            return Response(
                {'detail': 'Редактировать может только создатель записи.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
