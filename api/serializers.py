from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as JwtTokenObtainPairSerializers

User = get_user_model()

class TokenObtainPairSerializer(JwtTokenObtainPairSerializers):
    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add extra info to JWT response
        data.update({
            "id": self.user.id,
            "email": self.user.email,
            "role": self.user.role,
        })
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    username = None

    class Meta:
        model = User
        fields = ("email", "password", "role", "bio", "profile_picture",)

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role =validated_data.get("role", User.Roles.STUDENT),
            bio=validated_data.get("bio", ""),
            profile_picture=validated_data.get("profile_picture"),
        )
        return user
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "role", "bio", "profile_picture"]
