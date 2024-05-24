from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from api_auth.models import CustomUser


class PersonalInfo_List_CreateView_Validates_token():
    @classmethod
    def validate_token_for_user( request, *args, **kwargs):
        try:
            # Check if the access token is valid
            access_token = AccessToken(request.headers['Authorization'].split()[1])
        except InvalidToken:
            # Access token is invalid, return an error response
            return Response({"error": "Invalid access token"}, status=status.HTTP_401_UNAUTHORIZED)
        except TokenError as e:
            # Token error occurred, return an error response
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = CustomUser.objects.get(id=access_token["user_id"])
            if user.username == access_token['username'] and user.email == access_token['email']:
                return True
        except:
            user_data = {"user_id": access_token['user_id'], 
                         "username": access_token['username']}
            return Response(user_data, status=status.HTTP_404_NOT_FOUND)
