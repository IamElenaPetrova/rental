from django.core.exceptions import ValidationError

from fleet.models import Car

# =========================
# Common booking validation
# =========================


def validate_date_range(start_date, end_date) -> None:
    if start_date and end_date and start_date > end_date:
        raise ValidationError(
            'Start date cannot be later than end date.'
        )


def validate_no_overlaps(
    queryset,
    unit_filter: dict,
    start_date,
    end_date,
    exclude_booking_id=None,
    excluded_statuses=None,
) -> None:
    if not start_date or not end_date:
        return

    qs = queryset.filter(
        **unit_filter,
        start_date__lte=end_date,
        end_date__gte=start_date,
    )

    if excluded_statuses:
        qs = qs.exclude(status__in=excluded_statuses)

    if exclude_booking_id:
        qs = qs.exclude(pk=exclude_booking_id)

    if not qs.only('id').exists():
        return

    examples = (
        qs.select_related('renter')
        .only(
            'start_date',
            'end_date',
            'renter__first_name',
            'renter__last_name',
        )
        [:3]
    )

    parts = [
        f'{b.renter.last_name} {b.renter.first_name} '
        f'({b.start_date:%d.%m.%Y} - {b.end_date:%d.%m.%Y})'
        for b in examples
    ]

    raise ValidationError(
        'Overlaps with booking: ' + ', '.join(parts)
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


def validate_car_is_active(car_id) -> None:
    if car_id is None:
        return
    if not Car.objects.filter(pk=car_id, is_active=True).exists():
        raise ValidationError('Cannot create a booking for an inactive car.')
