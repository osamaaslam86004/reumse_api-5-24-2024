from rest_framework import serializers
from .models import CustomUser
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer




class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        # is_staff, is_active fields will used in serializing(Get user), and not in de-serializing (create/update user)
        # fields = ["id", 'email', 'username', 'password', "is_staff", "is_active",
        #           "locality", "facebook"]
        fields = ["id", 'email', 'username', 'password', "is_staff", "is_active"]
    def create(self, validated_data):

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            # is_staff = validated_data['is_staff'],
            # is_active = validated_data['is_active'],
            # locality = validated_data['locality'],
            # # start_date = validated_data['start_date'],
            # # end_date  = validated_data['end_date'],
            # facebook = validated_data['facebook']
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
        token['user'] = user.username

        return token