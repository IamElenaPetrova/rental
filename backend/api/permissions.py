from rest_framework import permissions


class IsCarOwnerOrAdmin(permissions.BasePermission):
    """
    Администратор (is_staff/is_superuser) — полный доступ.
    Иначе доступ только к объектам по машинам пользователя.
    Для Booking (obj.car), Expense (obj.car), Income (obj.booking.car).
    """

    def _get_car(self, obj):
        if hasattr(obj, 'car'):
            return obj.car
        if hasattr(obj, 'booking') and getattr(obj.booking, 'car', None):
            return obj.booking.car
        return None

    def _is_owner_or_admin(self, request, car):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if car is None:
            return False
        return car.owners.filter(pk=request.user.pk).exists()

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        car = self._get_car(obj)
        return self._is_owner_or_admin(request, car)
