from django.utils import timezone
from rest_framework import serializers

from bookings.models import Booking, Renter
from bookings.services import (
    format_overlapping_bookings_message,
    get_overlapping_bookings,
)


class RenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Renter
        fields = ('id', 'first_name', 'last_name', 'phone', 'comment', 'document')


class BookingReadSerializer(serializers.ModelSerializer):
    total_paid = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    renter = RenterSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = (
            'id',
            'car',
            'renter',
            'start_date',
            'end_date',
            'rent_amount',
            'total_paid',
            'currency',
            'status',
            'comment',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        )


class BookingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            'car',
            'renter',
            'start_date',
            'end_date',
            'rent_amount',
            'currency',
            'comment',
        )

    def to_representation(self, instance):
        return BookingReadSerializer(instance).data

    def validate(self, attrs):
        start = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        car = attrs.get('car', getattr(self.instance, 'car', None))

        if start and end and start > end:
            raise serializers.ValidationError(
                'Дата начала не может быть позже даты окончания.'
            )

        if car is not None:
            if not car.is_active:
                raise serializers.ValidationError(
                    'Нельзя создать бронирование для неактивного автомобиля.'
                )
            if not car.owners.exists():
                raise serializers.ValidationError(
                    'У автомобиля должен быть как минимум один владелец.'
                )
            request = self.context.get('request')
            if request and not (request.user.is_staff or request.user.is_superuser):
                if not car.owners.filter(pk=request.user.pk).exists():
                    raise serializers.ValidationError(
                        'Нельзя создать или изменить бронирование для чужой машины.'
                    )

        if start and start < timezone.now().date():
            raise serializers.ValidationError(
                'Дата начала не может быть в прошлом.'
            )

        if car and start and end:
            overlapping = get_overlapping_bookings(
                car=car,
                start_date=start,
                end_date=end,
                exclude_booking_id=self.instance.pk if self.instance else None,
            )
            if overlapping.exists():
                raise serializers.ValidationError(
                    format_overlapping_bookings_message(overlapping)
                )

        return attrs
