from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import fitopiaUser, Customer, Staff


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        max_length=100,
    )
    last_name = serializers.CharField(
        max_length=100,
    )
    username = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=fitopiaUser.objects.all())],
    )
    email = serializers.EmailField(
        max_length=200,
    )
    password = serializers.CharField(required=True, min_length=8)

    def create(self, validated_data):
        user = fitopiaUser(
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])  # Set the password
        user.save()  # Save the user instance
        return user

    class Meta:
        model = fitopiaUser
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
        )


class CustomerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    status = serializers.BooleanField(source="user.is_active", read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "email", "first_name", "last_name", "status"]


class StaffSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    status = serializers.BooleanField(source="user.is_active", read_only=True)

    class Meta:
        model = Staff
        fields = ["id", "email", "first_name", "last_name", "status"]
