from rest_framework import serializers
from api_auth.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "password", "is_staff", "is_active"]

    def create(self, validated_data):

        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
        )
        # refresh = RefreshToken.for_user(user)
        # tokens = {
        #     'refresh': str(refresh),
        #     'access': str(refresh.access_token)
        # }
        return user


class TokenClaimObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["user"] = user.username

        return token
