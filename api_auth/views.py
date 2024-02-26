from django.shortcuts import render
from rest_framework import viewsets
from api_auth.models import CustomUser
from api_auth.serializers import UserSerializer, TokenClaimObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.metadata import SimpleMetadata
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework.permissions import IsAuthenticated
from api_auth.custom_meta_data_class import CustomMetadata
import jsonschema  
from jsonschema import  ValidationError
from api_auth.schemas import user_create_request_schema, user_create_response_schema





class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenClaimObtainPairSerializer


class UserCreateView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    # metadata_class = SimpleMetadata
    # authentication_classes = [JWTStatelessUserAuthentication]
    # permission_classes = [IsAuthenticated]

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
            # Handle validation error
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except jsonschema.SchemaError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return response




    # def create(self, request, *args, **kwargs):
    #     if "metadata" in request.data:
    #         metadata = request.data.get('metadata')

    #     user_data = request.data.get('user_data')

    #     serializer = self.get_serializer(data=user_data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)

    #     CustomUser.objects.

    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
