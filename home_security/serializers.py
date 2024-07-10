from rest_framework import serializers

from .models import Apartment, Building, Entrance, User


class BuildingSerializer(serializers.ModelSerializer):
    manager = serializers.SlugRelatedField(
        read_only=True, slug_field="username", many=False
    )

    class Meta:
        model = Building
        fields = (
            "id",
            "number",
            "manager",
        )


class EntranceSerializer(serializers.ModelSerializer):
    guard = serializers.SlugRelatedField(
        read_only=True, slug_field="username", many=False
    )
    building = serializers.SlugRelatedField(
        read_only=True, slug_field="number", many=False
    )
    class Meta:
        model = Entrance
        fields = "__all__"


class ApartmentSerializer(serializers.ModelSerializer):
    entrance = serializers.SlugRelatedField(
        read_only=True, slug_field="number", many=False
    )
    class Meta:
        model = Apartment
        fields = "__all__"


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ("username", "password")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField()
