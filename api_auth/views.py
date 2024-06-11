# from django.shortcuts import render
from rest_framework import viewsets

# from rest_framework.views import APIView
from api_auth.models import CustomUser
from api_auth.serializers import UserSerializer, TokenClaimObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_control

# from rest_framework.metadata import SimpleMetadata
# from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
# from rest_framework.permissions import IsAuthenticated
# from api_auth.custom_meta_data_class import CustomMetadata
import jsonschema
from jsonschema import ValidationError
from api_auth.schemas import user_create_request_schema, user_create_response_schema

# from rest_framework.decorators import action
# import json
# from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from resume_api.custom_user_rated_throtle_class import (
    CustomUserRateThrottle,
    CustomAnonRateThrottle,
)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenClaimObtainPairSerializer


@method_decorator(cache_control(private=True), name="dispatch")
@method_decorator(cache_page(60 * 60 * 2), name="dispatch")
@method_decorator(vary_on_headers("User-Agent"), name="dispatch")
class UserCreateView(viewsets.ModelViewSet):
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
            jsonschema.validate(request.data, user_create_request_schema)

            # validate the type of each key e.g if is_active is boolean or not
        except jsonschema.ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # confirms if all the fields mentioned in "required fields" are present in request.data
        except jsonschema.SchemaError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # Create user
        response = super().create(request, *args, **kwargs)

        # Validate response data
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

    # def create(self, request, *args, **kwargs):
    #     if "metadata" in request.data:
    #         metadata = request.data.get('metadata')

    #     user_data = request.data.get('user_data')

    #     serializer = self.get_serializer(data=user_data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)

    #     CustomUser.objects.

    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
