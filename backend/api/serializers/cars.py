from rest_framework import serializers
from fleet.models import Car


class CarOwnerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)


class CarSerializer(serializers.ModelSerializer):
    owners = CarOwnerSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = ('id', 'name', 'plate_number', 'owners')
