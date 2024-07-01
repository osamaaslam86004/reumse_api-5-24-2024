import logging
import jwt
from django.conf import settings

# from rest_framework import serializers
from rest_framework import viewsets
from api_auth.models import CustomUser
from api_auth.serializers import UserSerializer, TokenClaimObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_control
import jsonschema
from jsonschema import ValidationError
from api_auth.schemas import (
    # user_create_request_schema,
    user_create_response_schema,
    ValidateJson,
)
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from api_auth.authentication import Custom_JWTStatelessUserAuthentication

# from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from resume_api.custom_user_rated_throtle_class import (
    CustomUserRateThrottle,
    CustomAnonRateThrottle,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    # BlacklistedToken,
)

logger = logging.getLogger(__name__)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenClaimObtainPairSerializer


@method_decorator(cache_control(private=True), name="dispatch")
@method_decorator(cache_page(60 * 60 * 2), name="dispatch")
@method_decorator(vary_on_headers("User-Agent"), name="dispatch")
class UserCreateView(viewsets.ModelViewSet, ValidateJson):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    http_method_names = [
        "post",
        "options",
    ]  # STATUS 200 FOR "OPTIONS" OR 405 METHOD NOT ALLOWED
    allowed_methods = ["POST", "OPTIONS"]  # RETURNED IN "ALLOW" HEADER
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    throttle_classes = [CustomAnonRateThrottle, CustomUserRateThrottle]
    lookup_url_kwarg = "id"

    def add_throttle_headers(self, request, response):
        response["X-RateLimit-Limit"] = request.rate_limit["X-RateLimit-Limit"]
        response["X-RateLimit-Remaining"] = request.rate_limit["X-RateLimit-Remaining"]

    def create(self, request, *args, **kwargs):
        # Validate request data
        try:
            self.validate_json(request.data)
        except Exception as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        response = super().create(request, *args, **kwargs)

        # # Validate response data
        try:
            jsonschema.validate(response.data, user_create_response_schema)
        except ValidationError as e:
            response = Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except jsonschema.SchemaError as e:
            response = Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        self.add_throttle_headers(request, response)

        return response

    def get_api_user_id_for_user(self, request, *args, **kwargs):

        if (
            "username" in request.data
            and "email" in request.data
            and "password" in request.data
            and request.data["username"]
            and request.data["email"]
            and request.data["password"] is not None
        ):
            username = request.data.get("username")
            email = request.data.get("email")
            password = request.data.get("password")

            print(username)
            print(email)
            print(password)

            try:
                queryset = CustomUser.objects.get_user(email, username, password)
                if queryset:
                    serializer = self.get_serializer(queryset)
                    response = Response(serializer.data)
                    self.add_throttle_headers(request, response)
                    return response

                else:
                    response = Response(
                        {"error": "User does not exist"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                    self.add_throttle_headers(request, response)
                    return response

            except Exception as e:
                response = Response({"error": str(e)})
                self.add_throttle_headers(request, response)
                return response
        else:
            return Response(
                {
                    "keys": "one of the keys is missing from list [username, password, username]",
                    "values": "either email is None or password is None",
                }
            )


class CheckOutstandingTokenView(APIView):
    authentication_classes = [Custom_JWTStatelessUserAuthentication]
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    throttle_classes = [CustomUserRateThrottle]
    http_method_names = ["post"]
    allowed_methods = ["POST"]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token not provided."}, status=400)

        try:
            # Decode the 'valid' refresh token to verify its authenticity, else raise exception
            # by token.check_black() method of RefreshToken class
            token = RefreshToken(refresh_token)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)

        # Decode the token manually to get the jti
        decoded_token = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms="HS256"
        )
        jti = decoded_token.get("jti")

        if not jti:
            return Response({"detail": "Invalid token."}, status=400)

        # Check if the token's jti is in the OutstandingToken list
        is_outstanding = OutstandingToken.objects.filter(jti=jti).exists()

        return Response(
            {
                "token": str(token),
                "is_outstanding": is_outstanding,
                "decoded_token": decoded_token,
            },
            status=200,
        )


class LogOutView(APIView):
    authentication_classes = [Custom_JWTStatelessUserAuthentication]
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    throttle_classes = [CustomUserRateThrottle]
    http_method_names = ["post"]
    allowed_methods = ["POST"]

    def post(self, request):
        """Blacklist the refresh token: extract token from the header
        during logout request user and refresh token is provided"""
        try:

            Refresh_token = request.data["refresh"]
            refresh_token = RefreshToken(Refresh_token)
            access = refresh_token.access_token

            is_active = request.user.is_active

            # Blacklist the outstanding refresh token
            # check and raise exception if token is "already" blacklisted
            refresh_token.blacklist()

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_200_OK)

        return Response(
            {
                "status": "Successful Logout",
                "is_active": str(is_active),
                "is_blacklisted": "True",
                "access": str(access),
            },
            status=status.HTTP_200_OK,
        )


# Notes:
#     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyMDE4NTI2OSwiaWF0IjoxNzE5MzIxMjY5LCJqdGkiOiJmMGI2YzhkYTI0NWY0YTU3OWYxZDlmMjQ0MDNhODNkZCIsInVzZXJfaWQiOjQsInVzZXIiOiJqd3R1c2VyMTIzNDUifQ.HBTzy3WKELqDjRi5wyru9hrV0h_ZV3HVWsaTwB-BULw",
#     "is_outstanding": true,
#     "decoded token": {
#         "token_type": "refresh",
#         "exp": 1720185269,
#         "iat": 1719321269,
#         "jti": "f0b6c8da245f4a579f1d9f24403a83dd",
#         "user_id": 4,
#         "user": "jwtuser12345"
#     }
# }
