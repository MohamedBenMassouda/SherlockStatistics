from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]

    def validate(self, attrs):
        # Check if the email is already in use
        email = attrs.get("email", None)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email is already in use")

        return attrs

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]