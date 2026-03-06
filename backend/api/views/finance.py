from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from finance.models import Expense
from api.permissions import IsCarOwnerOrAdmin
from api.serializers.finance import (
    ExpenseReadSerializer,
    ExpenseWriteSerializer,
    ExpensePhotoListSerializer,
)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related(
        'car', 'payed_by', 'created_by', 'updated_by'
    ).prefetch_related('photos')
    permission_classes = [permissions.IsAuthenticated, IsCarOwnerOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs.order_by('created_at')
        return qs.filter(car__owners=self.request.user).order_by('created_at')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ExpenseReadSerializer
        if self.action == 'upload_photos':
            return ExpensePhotoListSerializer
        return ExpenseWriteSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user, updated_by=user)

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(updated_by=user)

    @action(detail=True, methods=['post'], url_path='photos')
    def upload_photos(self, request, pk=None):
        """Загрузка фото к расходу. Multipart: поле photos — один или несколько файлов. Расход может не содержать фото (этот endpoint вызывается только при загрузке)."""
        expense = self.get_object()
        files = request.FILES.getlist('photos')
        if not files:
            return Response(
                {'photos': ['Нужно загрузить хотя бы одно фото.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ExpensePhotoListSerializer(data={'photos': files})
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            ExpensePhotoListSerializer.bulk_create_photos(
                expense, serializer.validated_data['photos']
            )
        expense = Expense.objects.prefetch_related('photos').get(pk=expense.pk)
        return Response(
            ExpenseReadSerializer(expense, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['delete'], url_path=r'photos/(?P<photo_pk>[^/.]+)')
    def delete_photo(self, request, pk=None, photo_pk=None):
        """Удаление одного фото расхода. DELETE /api/expenses/<id>/photos/<photo_id>/"""
        expense = self.get_object()
        photo = expense.photos.filter(pk=photo_pk).first()
        if not photo:
            return Response(
                {'detail': 'Фото не найдено или не принадлежит этому расходу.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        photo.delete()
        expense = Expense.objects.prefetch_related('photos').get(pk=expense.pk)
        return Response(
            ExpenseReadSerializer(expense, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )
