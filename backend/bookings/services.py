from .models import Booking


def get_overlapping_bookings(car, start_date, end_date, exclude_booking_id=None):
    """
    Queryset бронирований той же машины с пересекающимся периодом.
    Пересечение: start_new <= end_old AND end_new >= start_old.
    """
    qs = Booking.objects.filter(
        car=car,
        start_date__lte=end_date,
        end_date__gte=start_date,
    )
    if exclude_booking_id is not None:
        qs = qs.exclude(pk=exclude_booking_id)
    return qs


def format_overlapping_bookings_message(queryset):
    """
    Текст с именами арендаторов и датами пересекающихся бронирований.
    """
    parts = []
    for b in queryset:
        dates = f"{b.start_date:%d.%m.%Y} – {b.end_date:%d.%m.%Y}"
        parts.append(f"{b.renter_name} ({dates})")
    return "Пересечение с бронированием: " + ", ".join(parts)
