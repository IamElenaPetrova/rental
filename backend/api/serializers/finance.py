from decimal import Decimal

from rest_framework import serializers

from bookings.models import Currency
from core.constants import SYSTEM_BASE_CURRENCY
from finance.models import Income, IncomePhoto, Expense, ExpensePhoto


class IncomePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomePhoto
        fields = ('id', 'photo')


class IncomeReadSerializer(serializers.ModelSerializer):
    photos = IncomePhotoSerializer(many=True, read_only=True)
    received_by_display = serializers.SerializerMethodField()

    class Meta:
        model = Income
        fields = (
            'id',
            'booking',
            'received_date',
            'amount',
            'currency',
            'exchange_rate',
            'amount_in_booking_currency',
            'received_by',
            'received_by_display',
            'photos',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        )

    def get_received_by_display(self, obj):
        if not obj.received_by_id:
            return ''
        u = obj.received_by
        name = f'{u.first_name or ""} {u.last_name or ""}'.strip()
        return name or u.username


class IncomeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = (
            'received_date',
            'amount',
            'currency',
            'exchange_rate',
            'received_by',
        )

    def validate(self, attrs):
        booking = self.context.get('booking')
        if booking is None:
            raise serializers.ValidationError('Бронирование обязательно.')

        amount = attrs.get('amount')
        currency = attrs.get('currency')
        exchange_rate = attrs.get('exchange_rate')
        received_by = attrs.get('received_by')

        if amount is not None and amount <= 0:
            raise serializers.ValidationError('Сумма оплаты должна быть положительной.')

        car = booking.car
        if received_by and not car.owners.filter(pk=received_by.pk).exists():
            raise serializers.ValidationError(
                'Получатель должен быть владельцем автомобиля.'
            )

        if currency == booking.currency:
            attrs['exchange_rate'] = Decimal('1')
        else:
            if exchange_rate is None:
                raise serializers.ValidationError(
                    'exchange_rate обязателен, если валюта оплаты отличается '
                    'от валюты бронирования.'
                )
            if exchange_rate <= 0:
                raise serializers.ValidationError(
                    'Курс должен быть положительным.'
                )

        return attrs


class ExpensePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpensePhoto
        fields = ('id', 'photo')


class ExpenseReadSerializer(serializers.ModelSerializer):
    photos = ExpensePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = (
            'id',
            'car',
            'description',
            'date',
            'payed_by',
            'amount',
            'currency',
            'exchange_rate',
            'amount_in_base_currency',
            'base_currency_at_save',
            'photos',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        )


class ExpenseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = (
            'id',
            'car',
            'description',
            'date',
            'payed_by',
            'amount',
            'currency',
            'exchange_rate',
        )

    def validate(self, attrs):
        car = attrs.get('car', getattr(self.instance, 'car', None))
        payed_by = attrs.get('payed_by', getattr(self.instance, 'payed_by', None))

        if car is None:
            raise serializers.ValidationError('Автомобиль обязателен.')

        request = self.context.get('request')
        if request and not (request.user.is_staff or request.user.is_superuser):
            if not car.owners.filter(pk=request.user.pk).exists():
                raise serializers.ValidationError(
                    'Нельзя создать или изменить расход для чужой машины.'
                )

        if payed_by and not car.owners.filter(pk=payed_by.pk).exists():
            raise serializers.ValidationError(
                'Кто оплатил должен быть владельцем автомобиля.'
            )

        amount = attrs.get('amount')
        if amount is not None and amount <= 0:
            raise serializers.ValidationError(
                'Сумма расхода должна быть положительной.'
            )

        currency = attrs.get('currency')
        exchange_rate = attrs.get('exchange_rate')
        if currency and currency != SYSTEM_BASE_CURRENCY:
            if exchange_rate is None:
                raise serializers.ValidationError(
                    'exchange_rate обязателен, если валюта отличается от базовой.'
                )
            if exchange_rate <= 0:
                raise serializers.ValidationError(
                    'Курс должен быть положительным.'
                )

        return attrs


class ExpensePhotoListSerializer(serializers.Serializer):
    """Сериализатор загрузки фото расхода (только запись). Расход может не содержать фото."""

    photos = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False),
        allow_empty=False,
        write_only=True,
        error_messages={'empty': 'Нужно загрузить хотя бы одно фото.'},
    )

    @staticmethod
    def bulk_create_photos(expense, photos):
        ExpensePhoto.objects.bulk_create([
            ExpensePhoto(expense=expense, photo=photo)
            for photo in photos
        ])
