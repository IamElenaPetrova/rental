from rest_framework import viewsets, permissions

from fleet.models import Car
from api.serializers.cars import CarSerializer


class CarViewSet(viewsets.ReadOnlyModelViewSet):
    """Список машин пользователя (владелец или админ видит все)."""
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Car.objects.filter(is_active=True).prefetch_related('owners')
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs
        return qs.filter(owners=self.request.user)
