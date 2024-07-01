import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from tests.factories import UserFactory_Seializer_Testing
from api_auth.serializers import UserSerializer, TokenClaimObtainPairSerializer


CustomUser = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def build_user():
    """
    build user credentials randomly
    """

    def _build_user(**kwargs):
        return UserFactory_Seializer_Testing.build(**kwargs)

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

    return user_data, data


@pytest.mark.django_db
class TestUserSerializer:

    def test_serializer_deserialization(self, build_user):
        user = build_user()
        data = {
            "email": user.email,
            "username": user.username,
            "password": "testpassword",
            "is_active": user.is_active,
            "is_staff": user.is_staff,
        }
        serializer = UserSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()

        assert user.email == data["email"]
        assert user.username == data["username"]

    def test_serializer_serialization(self, create_user_using_api):

        user, data = create_user_using_api

        user_object = CustomUser.objects.get(id=data["id"])

        serializer = UserSerializer(instance=user_object)

        expected_fields = [
            "id",
            "email",
            "username",
            "is_staff",
            "is_active",
        ]
        import json

        assert set(serializer.data.keys()) == set(expected_fields)
        assert serializer.data["email"] == user_object.email
        assert serializer.data["username"] == user_object.username
        assert "password" not in serializer.data  # Ensure password is write_only

    def test_serializer_update_method(self, build_user):

        user = build_user()
        data = {
            "email": user.email,
            "username": user.username,
            "password": "testpassword",
            "is_active": user.is_active,
            "is_staff": user.is_staff,
        }
        serializer = UserSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()

        user = CustomUser.objects.get(email=data["email"])

        updated_data = {
            "email": "updated_user_email@example.com",
            "username": "updateduser_username",
            "password": "newpassword",
            "is_staff": False,
            "is_active": False,
        }

        serializer = UserSerializer(instance=user, data=updated_data)
        serializer.is_valid()
        updated_user = serializer.save()

        user.refresh_from_db()
        assert data["email"] != updated_user.email
        assert data["username"] != updated_user.username

    def test_serializer_validation(self):
        # Invalid data example
        invalid_data = {
            "email": "invalidemail",  # Invalid email format
            "username": "",
            "password": "short",  # Too short password
        }
        serializer = UserSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors
        assert "username" in serializer.errors
        assert not "password" in serializer.errors


@pytest.mark.django_db
class TestTokenClaimObtainPairSerializer:

    def test_missing_fields(self, create_user_using_api):
        user_factory, json_data = create_user_using_api

        data = {
            "username": json_data["username"],
            # Missing password
            "email": json_data["email"],
        }
        try:
            serializer = TokenClaimObtainPairSerializer(data=data)
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            assert "password" in e.detail
            assert e.detail["password"][0].code == "required"
