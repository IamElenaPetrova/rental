from django.core.exceptions import ValidationError


# =========================
# Common booking validation
# =========================

def validate_date_range(start_date, end_date) -> None:
    if start_date and end_date and start_date > end_date:
        raise ValidationError(
            'Start date cannot be later than end date.'
        )


def get_overlapping_bookings(
    queryset,
    unit_filter: dict,
    start_date,
    end_date,
    exclude_booking_id=None,
):
    """
    Universal overlap check:
    start_new <= end_old AND end_new >= start_old

    queryset: QuerySet of booking model (Booking / CarBooking / HouseBooking)
    unit_filter: {'car': car_obj} or {'house': house_obj} or {'car_id': 1}
    """
    qs = queryset.filter(
        **unit_filter,
        start_date__lte=end_date,
        end_date__gte=start_date,
    )
    if exclude_booking_id is not None:
        qs = qs.exclude(pk=exclude_booking_id)
    return qs


def format_overlapping_bookings_message(queryset) -> str:
    parts = []
    for booking in queryset:
        dates = f'{booking.start_date:%d.%m.%Y} - {booking.end_date:%d.%m.%Y}'
        parts.append(
            f'{booking.renter.last_name} {booking.renter.first_name} ({dates})'
        )
    return 'Overlaps with booking: ' + ', '.join(parts)


def validate_no_overlaps(
    queryset,
    unit_filter: dict,
    start_date,
    end_date,
    exclude_booking_id=None,
) -> None:
    overlapping = get_overlapping_bookings(
        queryset=queryset,
        unit_filter=unit_filter,
        start_date=start_date,
        end_date=end_date,
        exclude_booking_id=exclude_booking_id,
    )
    if overlapping.exists():
        raise ValidationError(
            format_overlapping_bookings_message(overlapping)
        )


# =========================
# Car-only validation
# =========================

def validate_mileage_range(start_mileage, end_mileage) -> None:
    if (
        start_mileage is not None
        and end_mileage is not None
        and end_mileage < start_mileage
    ):
        raise ValidationError(
            {
                'end_mileage': (
                    'End mileage must be greater than or equal to '
                    'start mileage.'
                )
            }
        )


def validate_car_is_active(car) -> None:
    if car is not None and not car.is_active:
        raise ValidationError(
            'Cannot create a booking for an inactive car.'
        )


def validate_car_has_owner(car) -> None:
    if car is not None and not car.owners.exists():
        raise ValidationError(
            'A car must have at least one owner.'
        )


def validate_user_can_manage_car_booking(user, car) -> None:
    if user and not (user.is_staff or user.is_superuser):
        if car is not None and not car.owners.filter(pk=user.pk).exists():
            raise ValidationError(
                'You cannot create or update a booking for a car '
                'you do not own.'
            )
