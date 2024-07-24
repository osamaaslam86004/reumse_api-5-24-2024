import pytest

# import jwt
import json

# from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import UserFactory
from api_auth.models import CustomUser


# @pytest.mark.django_db
# Use Sparingly: Only use @pytest.mark.django_db when necessary. For tests that do not require database access
# (e.g., pure unit tests), avoid using this decorator to keep those tests fast and isolated.

# Factory Libraries:
# Use libraries like factory_boy or pytest-factoryboy to create test data efficiently.

# Fixtures:
# Use pytest fixtures for setting up common test data, reducing redundancy and improving test readability.


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def build_user():
    """
    build user credentials randomly
    """

    def _build_user(**kwargs):
        return UserFactory.build(**kwargs)

    return _build_user


@pytest.fixture
def create_user_using_api(api_client, build_user):
    """
    create a user by sending a post request to 'crud-user' endpoint, and then return user credentials
    """
    user = build_user()

    user_data = {
        "email": user.email,
        "username": user.username,
        "password": user.password,
    }

    headers = {"Origin": "https://web.postman.co"}
    response = api_client.post(
        reverse("crud-user-list"), user_data, headers=headers, format="json"
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "password" not in data

    # Validate that the user was actually created in the database
    user = CustomUser.objects.get(email=user_data["email"])
    assert user.username == user_data["username"]

    return user_data


@pytest.fixture
def get_refresh_and_access_tokens_for_user(api_client):
    def _get_refresh_and_access_tokens_for_user(data):
        """
        Get and return the refresh and access tokens for a given user with credentials in the argument 'data'
        """

        headers = {"Origin": "https://web.postman.co"}

        response = api_client.post(
            reverse("token_obtain_pair"), data=data, headers=headers, format="json"
        )

        assert response.status_code == 200
        assert "access" in response.json()
        assert "refresh" in response.json()

        return response.json()

    return _get_refresh_and_access_tokens_for_user


@pytest.mark.django_db
class Test_API_Endpoint_Throttling_Headers_Values:
    """
    Test class to test API endpoint "crud-user-list" for headers linked throttling
    """

    def test_throttling_settings_for_endpoint(self):
        # Create an API client
        client = APIClient()

        headers = {"Origin": "https://web.postman.co"}

        # Send multiple requests to the endpoint
        for _ in range(2):
            user = UserFactory.build()
            # Prepare the data dictionary, accoring to jsonschema
            data = {
                "email": user.email,
                "username": user.username,
                "password": user.password,
            }

            response = client.post(
                reverse("crud-user-list"), headers=headers, data=data, format="json"
            )

            # Assert the response status code
            assert response.status_code == 201
            assert response["X-RateLimit-Limit"] == "2/hour"
            assert response["X-RateLimit-Remaining"] == f"{1 - _}"

        # # Send one more request to the endpoint
        response = client.post(
            reverse("crud-user-list"), headers=headers, data=data, format="json"
        )

        for header in response.headers:
            print(f"header name : {header}------------ : {response.headers[header]}")

        # Assert the response status code
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "X-RateLimit-Limit" not in response.headers
        assert "X-RateLimit-Remaining" not in response.headers

        # Assert the throttling limit
        assert "Retry-After" in response


@pytest.mark.django_db
class TestAPIEndpointThrottling_Rates_For_Authenticated_Users:
    """
    Test class to test API endpoint "crud-user-list" for throttling rate limit settings
    for authenticated users.
    """

    def test_throttling_settings_for_endpoint1(self, api_client, build_user):
        user = build_user()

        # Create user and get user credentials first ==> Ist request
        data = {
            "email": user.email,
            "username": user.username,
            "password": user.password,
        }

        headers = {"Origin": "https://web.postman.co"}

        response = api_client.post(
            reverse("crud-user-list"),
            headers=headers,
            data=data,
            format="json",
        )

        user = CustomUser.objects.get(id=response.json()["id"])
        username = user.username

        # Authenticate user
        api_client.force_authenticate(user=user)

        # Send 2 more requests to the endpoint ending the throttling quta

        for _ in range(2):

            response = api_client.post(
                reverse("get_api_user_id_for_user"),
                headers=headers,
                data=data,
                format="json",
            )
            assert response["X-RateLimit-Limit"] == "3/hour"
            assert response["X-RateLimit-Remaining"] == f"{2 - _}"
            assert username == response.json()["username"]

            # Assert the response status code
            if _ == 2:
                assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

                # Assert the throttling limit
                assert "Retry-After" in response


@pytest.mark.django_db
class Test_API_Endpoint_Throttling_Rates_For_UnAuthenticated_Users:
    """
    Test class to test API endpoint "crud-user-list" for throttling rate limit settings
    for un-authenticated users.
    """

    def test_throttling_settings_for_endpoint1(self, api_client, build_user):

        headers = {"Origin": "https://web.postman.co"}
        user = build_user()

        # Create user and get user credentials first ==> Ist request
        data = {
            "email": user.email,
            "username": user.username,
            "password": user.password,
        }

        # Send 2 requests to the endpoint ending the throttling quta
        for _ in range(2):

            response = api_client.post(
                reverse("get_api_user_id_for_user"),
                data=data,
                headers=headers,
                format="json",
            )
            print(f"User------------- : {response.json()}")

            assert response.json() == {"error": "User does not exist"}
            assert response["X-RateLimit-Limit"] == "2/hour"
            assert response["X-RateLimit-Remaining"] == f"{1 - _}"

            # Assert the response status code
            if _ == 2:
                assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

                # Assert the throttling limit
                assert "Retry-After" in response


@pytest.mark.django_db
class Test_UserCreateView_For_Cache:
    def test_cache_headers(self, api_client, build_user):

        # build user data using the factory
        user = build_user()

        # Prepare the data dictionary, accoring to jsonschema
        data = {
            "email": user.email,
            "username": user.username,
            "password": user.password,
        }

        # Send a POST request to the endpoint
        headers = {"Origin": "https://web.postman.co", "Accept": "application/json"}
        url = "https://osamaaslam.pythonanywhere.com/api/auth/crud-user/"
        response = api_client.post(url, data=data, headers=headers, format="json")
        # Assert the response status code
        assert response.status_code == status.HTTP_201_CREATED

        # Check cache control headers
        assert response.headers.get("Cache-Control") == "private"
        assert response.headers.get("Vary") == "User-Agent"

        # Check the presence of cache headers
        assert "Cache-Control" in response.headers
        assert "Vary" in response.headers

        # Check that Cache-Control is set to private
        assert "private" in response.headers["Cache-Control"]


@pytest.mark.django_db
class Test_Options_Request_For_UserCreateView_For_Cache_Related_Headers:
    def test_options_request(self, api_client):
        # Send a POST request to the endpoint
        headers = {"Origin": "https://web.postman.co", "Accept": "application/json"}
        response = api_client.options(
            reverse("crud-user-list"), headers=headers, format="json"
        )

        # Assert status code is 200 OK for OPTIONS request
        assert response.status_code == status.HTTP_200_OK

        # Check cache control headers
        assert response.headers.get("Cache-Control") == "private"
        assert response.headers.get("Vary") == "User-Agent"

        # Check the presence of cache headers
        assert "Cache-Control" in response.headers
        assert "Vary" in response.headers

        # Check that Cache-Control is set to private
        assert "private" in response.headers["Cache-Control"]

        # Check Allow header
        assert response.headers.get("Allow") == "POST, OPTIONS"


class Test_UserCreateView_for_allowed_methods_in_allow_header:
    """
    tests to check allow http methods by endpoint / router "crud-user"
    """

    def test_allowed_methods_in_allow_header_for_crud_user(self):
        # Create an API client
        client = APIClient()

        # Send an OPTIONS request to the endpoint
        headers = {"Origin": "https://web.postman.co"}
        response = client.options(reverse("crud-user-list"), headers=headers)

        # Assert the response status code
        assert response.status_code == status.HTTP_200_OK

        # Assert the allowed methods
        assert "POST" and "OPTIONS" in response.headers["Allow"]
        # for non-CORS
        assert len(response.headers["Allow"].split(", ")) == 2
        # for CORS
        assert len(response.headers["Access-Control-Allow-Methods"].split(", ")) == 2


class Test_UserCreateView_origin_header_in_options_request:
    """
    tests to check Cross-Origin-Resource-sharing for provided Origin is allowed
    """

    def test_origin_header_in_options_request_for_crud_user(self):
        # Create an API client
        client = APIClient()

        # Send a POST request to the endpoint
        response = client.options(reverse("crud-user-list"), format="json")

        # Assert the response status code
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Origin not allowed"

        byte_string = response.content  # b'{"detail":"Origin not trusted"}'
        unicode_string = byte_string.decode(
            "utf-8"
        )  # Decode byte string to Unicode string
        python_dict = json.loads(unicode_string)  # Parse Unicode string as JSON
        assert python_dict == {"detail": "Origin not allowed"}


@pytest.mark.django_db
class Test_TokenObtainPairView:
    """
    tests if endpoint '/token/ correctly generate a refresh,  access tokens
    """

    def test_token_obtain_pair(self, api_client, create_user_using_api):

        headers = {"Origin": "https://web.postman.co"}

        data = {
            "email": create_user_using_api["email"],
            "password": create_user_using_api["password"],
        }

        response = api_client.post(
            reverse("token_obtain_pair"), data=data, headers=headers, format="json"
        )

        assert response.status_code == 200
        assert "access" in response.json()
        assert "refresh" in response.json()


@pytest.mark.django_db
class Test_TokenVerifyView:
    """
    tests if endpoint 'token/verify/ correctly validates a generated access token
    """

    def test_token_verification(
        self, api_client, create_user_using_api, get_refresh_and_access_tokens_for_user
    ):

        # Create user and get user credentials first
        data = {
            "email": create_user_using_api["email"],
            "password": create_user_using_api["password"],
        }

        # Get the tokens for this user
        tokens = get_refresh_and_access_tokens_for_user(data)
        headers = {"Origin": "https://web.postman.co"}

        # Make a request to the verify endpoint with the token
        api_client = APIClient()
        response = api_client.post(
            reverse("token_verify"),
            {"token": tokens["access"]},
            headers=headers,
            format="json",
        )

        # Assertions
        assert response.status_code == 200
        assert response.json() == {}, "Expected an empty response"


@pytest.mark.django_db
class Test_RefreshToken_get_new_access_token:
    """
    tests if endpoint '/token/refresh/' is generating a access tokens for a given refresh token
    """

    def test_token_verification(
        self, api_client, create_user_using_api, get_refresh_and_access_tokens_for_user
    ):

        # Create user and get user credentials first
        data = {
            "email": create_user_using_api["email"],
            "password": create_user_using_api["password"],
        }

        # Get the tokens for this user
        tokens = get_refresh_and_access_tokens_for_user(data)
        headers = {"Origin": "https://web.postman.co"}

        # Make a request to the verify endpoint with the token
        response = api_client.post(
            reverse("token_refresh"),
            {"refresh": tokens["refresh"]},
            headers=headers,
            format="json",
        )

        # Assertions
        # print(response.content)
        assert response.status_code == 200
        assert "access" in response.json()
        assert not "refresh" in response.json()

        new_access_token = response.json()["access"]

        # check if new access token is diffrent from old access token ==> endpoint is Ok!
        assert new_access_token != tokens["access"]


@pytest.mark.django_db
class Test_UserCreateView_test_post_method_for_crud_user:
    """
    test if crud-user-list is creating user successfully
    """

    def test_post_method_for_crud_user(self, build_user):
        # Create an API client
        client = APIClient()

        # First, we check if application/json is allowed and Origin is allowed in a preflight request
        headers = {"Origin": "https://web.postman.co", "Accept": "application/json"}

        response = client.options(reverse("crud-user-list"), headers=headers)
        assert "Allow" in response.headers
        # for CORS
        assert len(response.headers["Access-Control-Allow-Methods"].split(", ")) == 2
        assert response.headers["Content-Type"] == "application/json"
        # Assert the response status code
        assert response.status_code == status.HTTP_200_OK

        # build user data using the factory
        user = build_user()

        # Prepare the data dictionary, accoring to jsonschema
        data = {
            "email": user.email,
            "username": user.username,
            "password": user.password,
        }

        # Send a POST request to the endpoint
        headers = {"Origin": "https://web.postman.co", "Accept": "application/json"}
        response = client.post(
            reverse("crud-user-list"), data=data, headers=headers, format="json"
        )
        # Assert the response status code
        assert response.status_code == status.HTTP_201_CREATED

        # Getting the actual JSON response received from an API call
        actual_response = response.data

        # Assert the expected keys in JSON data matches the keys in actual JSON response
        assert (
            "id"
            and "username"
            and "email"
            and "is_active"
            and "is_staff" in actual_response
            and len(actual_response) == 5
        )


@pytest.mark.django_db
class Test_GetAPIUserIDForUser:
    """
    get the id of user from the API server, if password, username, email is provided
    """

    def test_post_request_for_api_user_id_for_user(
        self, api_client, create_user_using_api
    ):

        data = {
            "email": create_user_using_api["email"],
            "username": create_user_using_api["username"],
            "password": create_user_using_api["password"],
        }

        # Send a POST request to the endpoint
        headers = {"Origin": "https://web.postman.co", "Accept": "application/json"}

        response = api_client.post(
            reverse("get_api_user_id_for_user"),
            data=data,
            headers=headers,
            format="json",
        )

        assert response.status_code == 200
        actual_response = response.json()
        print(f"keys------------- : {actual_response}")
        expected_keys = {
            "id",
            "username",
            "email",
            "is_staff",
            "is_active",
        }

        for key in expected_keys:
            assert key in actual_response, f"Missing key: {key}"

        assert len(actual_response) == len(expected_keys)


# class Test_Manually_Verify_Access_Token_View:
#     """
#     tests for manually validating a generated access token
#     """

#     def Manually_Verify_Access_Token_View(self, access_token):
#         # Decode the JWT token
#         decoded_token = jwt.decode(
#             access_token, settings.SECRET_KEY, algorithms=["HS256"]
#         )
#         print(f"decoded---token : {decoded_token}")

#         # Assert custom claims
#         assert decoded_token["user"] == "test110"
#         assert decoded_token["token_type"] == "access"
