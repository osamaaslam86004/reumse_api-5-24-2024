# from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from api_auth.models import CustomUser
from api_auth.serializers import UserSerializer, TokenClaimObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
# from rest_framework.metadata import SimpleMetadata
# from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
# from rest_framework.permissions import IsAuthenticated
# from api_auth.custom_meta_data_class import CustomMetadata
import jsonschema
from jsonschema import  ValidationError
from api_auth.schemas import user_create_request_schema, user_create_response_schema
from rest_framework.decorators import action
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View





class checking_status(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serializer_class = None

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                # Validate schema if needed (refer to external resources for schema validation)
                # if not validate_schema(data):
                #     return HttpResponseBadRequest({'message': 'Invalid JSON schema'})

                # Assuming no external API call is required (based on prompt instructions)
                # Process data or perform any necessary actions here

                return JsonResponse({'response_content': data, 'headers': {'Content-type': 'application/json'}})
            except json.JSONDecodeError:
                return HttpResponseBadRequest({'message': 'Invalid JSON data'})
        else:
            return JsonResponse({'message': 'Method not allowed'}, status=405)

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            try:
                data = {"key" : "value"}
                return JsonResponse({'response_content': data, 'headers': {'Content-type': 'application/json'}})
            except json.JSONDecodeError:
                return HttpResponseBadRequest({'message': 'Invalid JSON data'})
        else:
            return JsonResponse({'message': 'Method not allowed'}, status=405)







class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenClaimObtainPairSerializer


class UserCreateView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


    def list(self, request, *args, **kwargs):
        return Response(data = {"error" : "Method not allowed"})

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

    @action(detail=False, methods=['POST'])
    def get_api_user_id_for_user(self, request, *args, **kwargs):

        if 'username' in request.data and 'email' in request.data and 'password' in request.data and request.data['username'] and request.data['email'] and request.data['password'] is not None:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')

            print(username)
            print(email)
            print(password)

            try:
                queryset = CustomUser.objects.get_user(email, username, password)
                if queryset:
                    serializer = self.get_serializer(queryset)
                    return Response(serializer.data)
                else:
                    return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error":str(e)})
        else:
            return Response({"keys" : "one of the keys is missing from list [username, password, username]",
                             "values" : "either email is None or password is None"})












    # def create(self, request, *args, **kwargs):
    #     if "metadata" in request.data:
    #         metadata = request.data.get('metadata')

    #     user_data = request.data.get('user_data')

    #     serializer = self.get_serializer(data=user_data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)

    #     CustomUser.objects.

    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
