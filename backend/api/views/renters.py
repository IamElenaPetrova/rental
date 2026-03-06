from rest_framework import viewsets, permissions

from bookings.models import Renter
from api.serializers.bookings import RenterSerializer


class RenterViewSet(viewsets.ModelViewSet):
    queryset = Renter.objects.all().order_by('last_name', 'first_name')
    serializer_class = RenterSerializer
    permission_classes = [permissions.IsAuthenticated]
