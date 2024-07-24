import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import UserFactory
from tests.factories import (
    UserFactory,
    PersonalInfoFactory,
    OverviewFactory,
    JobAccomplishmentFactory,
    JobFactory,
    EducationFactory,
    SkillAndSkillLevelFactory,
    ProgrammingAreaFactory,
    ProjectsFactory,
    PublicationFactory,
)
from resume.models import PersonalInfo
import requests_mock
from api_auth.models import CustomUser
from resume.models import (
    PersonalInfo,
    Overview,
    Education,
    Job,
    JobAccomplishment,
    SkillAndSkillLevel,
    ProgrammingArea,
    Projects,
    Publication,
)

# Signature ==> api_client.post( (reverse(url, {**kwargs} ), headers, data, format)

# select_related: when the object that you're going to be selecting is a single object, so OneToOneField or a ForeignKey

# prefetch_related: when you're going to get a "set" of things, so ManyToManyFields as you stated or reverse ForeignKeys.


keys_list = [
    "id",
    "user_id",
    "first_name",
    "middle_name",
    "last_name",
    "suffix",
    "locality",
    "region",
    "title",
    "email",
    "linkedin",
    "facebook",
    "github",
    "site",
    "twittername",
    "overview",
    "education",
    "job",
    "skill",
    "programming_area",
    "projects",
    "publications",
]



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
def Manually_Verify_Access_Token():
    def _Manually_Verify_Access_Token(access_token):

        import jwt
        from django.conf import settings

        # Decode the JWT token
        decoded_token = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        print(f"decoded---token : {decoded_token}")

        # Assert custom claims
        assert "user_id" in decoded_token and "user" in decoded_token
        assert decoded_token["token_type"] == "access"

        return decoded_token

    return _Manually_Verify_Access_Token


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


@pytest.fixture
def create_access_token_for_user(
    api_client, create_user_using_api
):  # ===> fixtures are passed as arguments
    def _create_access_token(**kwargs):

        user_data, data = create_user_using_api  # ==> dict object not callable

        user = CustomUser.objects.get(id=data["id"])

        data = {
            "email": data["email"],
            "password": user_data["password"],
        }

        print(f"uaer authenticated -------- : {user.is_authenticated}")

        headers = {"Origin": "https://web.postman.co"}

        response = api_client.post(
            reverse("token_obtain_pair"), data=data, headers=headers, format="json"
        )

        assert response.status_code == 200
        assert "access" in response.json()
        assert "refresh" in response.json()

        return response.json(), user

    return _create_access_token


@pytest.fixture
def personal_info_data():
    def _personal_info_data(user):

        personal_info_instance = PersonalInfoFactory.build(user_id=user)
        overview_instance = OverviewFactory.build()
        education_instances = [EducationFactory.build() for _ in range(2)]
        job_instance = JobFactory.build()
        job_accomplishment_instance = JobAccomplishmentFactory.build()
        skill_and_skill_level_instances = SkillAndSkillLevelFactory.build()
        programming_area_instances = ProgrammingAreaFactory.build()
        projects_instances = [ProjectsFactory.build() for _ in range(2)]
        publication_instances = [PublicationFactory.build() for _ in range(2)]

        json_data = {
            "first_name": personal_info_instance.first_name,
            "middle_name": personal_info_instance.middle_name,
            "last_name": personal_info_instance.last_name,
            "suffix": personal_info_instance.suffix,
            "locality": personal_info_instance.locality,
            "region": personal_info_instance.region,
            "title": personal_info_instance.title,
            "email": personal_info_instance.email,
            "linkedin": personal_info_instance.linkedin,
            "facebook": personal_info_instance.facebook,
            "github": personal_info_instance.github,
            "site": personal_info_instance.site,
            "twittername": personal_info_instance.twittername,
            "overview": {
                "text": overview_instance.text,
            },
            "education": [
                {
                    "name": instance.name,
                    "location": instance.location,
                    "schoolurl": instance.schoolurl,
                    # factoryboy already created this field in ISO Format
                    "education_start_date": instance.education_start_date,
                    "education_end_date": instance.education_end_date,
                    "degree": instance.degree,
                    "description": instance.description,
                }
                for instance in education_instances
            ],
            "job": {
                "company": job_instance.company,
                "companyurl": job_instance.companyurl,
                "location": job_instance.location,
                "title": job_instance.title,
                "description": job_instance.description,
                "job_start_date": job_instance.job_start_date,
                "job_end_date": job_instance.job_end_date,
                "is_current": job_instance.is_current,
                "is_public": job_instance.is_public,
                "image": job_instance.image,
                "accomplishment": {
                    "job_accomplishment": job_accomplishment_instance.job_accomplishment,
                },
            },
            "skill": [
                {
                    "text": skill_and_skill_level_instances.text,
                    "skill_level": skill_and_skill_level_instances.skill_level,
                }
            ],
            "programming_area": [
                {
                    "programming_area_name": programming_area_instances.programming_area_name,
                    "programming_language_name": programming_area_instances.programming_language_name,
                }
            ],
            "projects": [
                {
                    "project_name": instance.project_name,
                    "short_description": instance.short_description,
                    "long_description": instance.long_description,
                    "link": instance.link,
                }
                for instance in projects_instances
            ],
            "publications": [
                {
                    "title": instance.title,
                    "authors": instance.authors,
                    "journal": instance.journal,
                    "year": instance.year,
                    "link": instance.link,
                }
                for instance in publication_instances
            ],
        }

        return json_data, personal_info_instance, user

    return _personal_info_data


@pytest.fixture
def create_personal_info_instance_using_api(
    api_client, personal_info_data, create_access_token_for_user
):
    def _create_personal_info_instance_using_api():
        # Create user, and get the access token for the created user
        tokens, user= create_access_token_for_user()

        json_data, personal_info_instance, user = personal_info_data(user)

        # create user
        json_data["user_id"] = user.id
        # print(f"json data before sending to post ------------ :{json_data}")

        # set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {tokens["access"]}",
        }

        response = api_client.post(
            reverse("get-personal-info-data-list"),
            data=json_data,
            headers=headers,
            format="json",
        )

        assert response.status_code == 201
        # print(f"response in personal info data using api -------- : {response.json()}")

        return response.json(), tokens

    return _create_personal_info_instance_using_api



@pytest.fixture
def fetching_data_from_database_and_create_JSON():
    def _fetching_data_from_database_and_create_JSON(id):
        """
        Manually created Json data according to endpoint Schema by fetching personal_info_instance 
        from datastore
        """
        from django.db.models import Prefetch
        # select_related: 
        # when the object that you're going to be selecting is a single object, so OneToOneField or a ForeignKey
        # prefetch_related:
        #  when you're going to get a "set" of things, so ManyToManyFields as you stated or reverse ForeignKeys.
        
        personal_info_instance = PersonalInfo.objects.prefetch_related(
            Prefetch('overview'),
            Prefetch('job'),
            Prefetch('job__accomplishment'),
            Prefetch('education', queryset=Education.objects.all()),
            Prefetch('skill', queryset=SkillAndSkillLevel.objects.all()),
            Prefetch('programming_area', queryset=ProgrammingArea.objects.all()),
            Prefetch('projects', queryset=Projects.objects.all()),
            Prefetch('publications', queryset=Publication.objects.all()),
            ).get(id=id)
        
        overview_instance = personal_info_instance.overview
        education_instances = personal_info_instance.education.all()
        job_instance = personal_info_instance.job
        job_accomplishment_instance = job_instance.accomplishment
        skill_and_skill_level_instances = personal_info_instance.skill.all()
        programming_area_instances = personal_info_instance.programming_area.all()
        projects_instances = personal_info_instance.projects.all()
        publication_instances = personal_info_instance.publications.all()

        json_data = {
            "first_name": personal_info_instance.first_name,
            "middle_name": personal_info_instance.middle_name,
            "last_name": personal_info_instance.last_name,
            "suffix": personal_info_instance.suffix,
            "locality": personal_info_instance.locality,
            "region": personal_info_instance.region,
            "title": personal_info_instance.title,
            "email": personal_info_instance.email,
            "linkedin": personal_info_instance.linkedin,
            "facebook": personal_info_instance.facebook,
            "github": personal_info_instance.github,
            "site": personal_info_instance.site,
            "twittername": personal_info_instance.twittername,
            "overview": {
                "text": overview_instance.text,
            }, 
            "education": [
                {
                    "name": instance.name,
                    "location": instance.location,
                    "schoolurl": instance.schoolurl,
                    # factoryboy already created this field in ISO Format
                    "education_start_date": instance.education_start_date,
                    "education_end_date": instance.education_end_date,
                    "degree": instance.degree,
                    "description": instance.description,
                }
                for instance in education_instances
            ],
            "job": {
                "company": job_instance.company,
                "companyurl": job_instance.companyurl,
                "location": job_instance.location,
                "title": job_instance.title,
                "description": job_instance.description,
                "job_start_date": job_instance.job_start_date,
                "job_end_date": job_instance.job_end_date,
                "is_current": job_instance.is_current,
                "is_public": job_instance.is_public,
                "image": job_instance.image,
                "accomplishment": {
                    "job_accomplishment": job_accomplishment_instance.job_accomplishment,
                },
            },
            "skill": [
                {
                    "text": instance.text,
                    "skill_level": instance.skill_level,
                } for instance in skill_and_skill_level_instances
            ],
            "programming_area": [
                {
                    "programming_area_name": instance.programming_area_name,
                    "programming_language_name": instance.programming_language_name,
                } for instance in programming_area_instances
            ],
            "projects": [
                {
                    "project_name": instance.project_name,
                    "short_description": instance.short_description,
                    "long_description": instance.long_description,
                    "link": instance.link,
                }
                for instance in projects_instances
            ],
            "publications": [
                {
                    "title": instance.title,
                    "authors": instance.authors,
                    "journal": instance.journal,
                    "year": instance.year,
                    "link": instance.link,
                }
                for instance in publication_instances
            ],
        }

        return json_data
    return _fetching_data_from_database_and_create_JSON




@pytest.fixture
def manually_created_data():
    json_data = {
        "first_name": "John",
        "middle_name": "A.",
        "last_name": "Doe",
        "suffix": "PhD",
        "locality": "Boston",
        "region": "MA",
        "title": "Developer",
        "email": "john.doe@example.com",
        "linkedin": "https://linkedin.com/in/johndoe",
        "facebook": "https://facebook.com/johndoe",
        "github": "https://github.com/johndoe",
        "site": "https://johndoe.com",
        "twittername": "johndoe",
        "overview": {
            "text": "John Doe is a seasoned developer with a PhD in Computer Science...",
        },
        "education": [
            {
                "name": "Harvard University",
                "location": "Cambridge, MA",
                "schoolurl": "https://harvard.edu",
                "education_start_date": "2010-09-01",
                "education_end_date": "2014-06-01",
                "degree": "BSc in Computer Science",
                "description": "Studied various aspects of computer science including algorithms, data structures, and artificial intelligence.",
            }
        ],
        "job": {
            "company": "Tech Corp",
            "companyurl": "https://techcorp.com",
            "location": "San Francisco, CA",
            "title": "Senior Developer",
            "description": "Worked on developing scalable web applications.",
            "job_start_date": "2015-07-01",
            "job_end_date": "2020-12-01",
            "is_current": False,
            "is_public": True,
            "image": "path/to/company/image.png",
            "accomplishment": {
                "job_accomplishment": "Led a team of developers to create a new e-commerce platform.",
            },
        },
        "skill": [
            {"text": "Python", "skill_level": "Expert"},
            {"text": "Django", "skill_level": "Advanced"},
        ],
        "programming_area": [
            {
                "programming_area_name": "BACKEND",
                "programming_language_name": "Python (Django)",
            },
            {
                "programming_area_name": "FRONTEND",
                "programming_language_name": "JavaScript",
            },
        ],
        "projects": [
            {
                "project_name": "E-commerce Platform",
                "short_description": "Developed a full-featured e-commerce platform.",
                "long_description": "Developed a full-featured e-commerce platform with user authentication, product management, and payment processing.",
                "link": "https://github.com/johndoe/ecommerce-platform",
            }
        ],
        "publications": [
            {
                "title": "Research on AI Algorithms",
                "authors": "John Doe, Jane Smith",
                "journal": "Journal of AI Research",
                "year": 2019,
                "link": "https://journals.org/ai-research/johndoe2019",
            }
        ],
    }
    return json_data



@pytest.mark.django_db
class Test_PersonalInfo_For_Throttling_For_Authenticated_Users:
    """
    Test class to test API endpoint ""get-personal-info-data-list" for headers linked throttling
    for authenticated user
    """

    def test_throttling_settings_for_endpoint1(
        self,
        api_client,
        create_access_token_for_user,
        Manually_Verify_Access_Token,
        manually_created_data,
    ):

        # Create the user first! and then get the access token for the created user
        tokens, user = create_access_token_for_user()
        access_token = tokens["access"]

        # set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {access_token}",
        }

        decoded_token = Manually_Verify_Access_Token(access_token)

        user = CustomUser.objects.get(id=decoded_token["user_id"])

        # Send multiple requests to the endpoint
        for _ in range(3):

            response = api_client.get(
                reverse("get_personal_info_for_user") + f"?user_id={user.id}",
                data=manually_created_data,
                headers=headers,
                format="json",
            )
            # Assert the response status code
            if _ == 3:
                assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
                assert "X-RateLimit-Limit" not in response.headers
                assert "X-RateLimit-Remaining" not in response.headers

                # Assert the throttling limit
                assert "Retry-After" in response
            else:
                # print(f"response--------------: {response.json()}")

                assert response.status_code == 200
                assert response.json() == []

                assert response["X-RateLimit-Limit"] == "3/hour"
                assert response["X-RateLimit-Remaining"] == f"{2 - _}"

                # for header in response.headers:
                #     print(
                #         f"header name : {header}------------ : {response.headers[header]}"
                #     )


@pytest.mark.django_db
class Test_PersonalInfo_For_Un_Authenticated_User:
    """
    Test class to test API endpoint ""get-personal-info-data-list" for Un-authenticated user
    Remember authentication is performed first : before throttling and other settings
    """

    def test_throttling_settings_for_endpoint1(
        self,
        manually_created_data,
        api_client,
    ):
        # set the access token in headers
        headers = {"Origin": "https://web.postman.co"}

        json_data = manually_created_data

        response = api_client.post(
            reverse("get-personal-info-data-list"),
            data=json_data,
            headers=headers,
            format="json",
        )
        data = response.json()
        print(f"data----------- {data}")
        assert data == {"detail": "Authentication credentials were not provided."}
        assert response.headers["WWW-Authenticate"] == 'Bearer realm="api"'
        assert response.status_code == 401

        # for header in response.headers:
        #     print(f"header name : {header}------------ : {response.headers[header]}")



@pytest.mark.django_db
class Test_Options_Request_For_PersonalInfo_For_Cache_Related_Headers:
    """
    test to chceck if cache related headers are present in response headers
    """
    def test_options_request(self, api_client, create_personal_info_instance_using_api):

        # Create PersonalInfo instance by creating a user, and getting the jwt token
        response_from_personal_info , tokens = create_personal_info_instance_using_api()

        # retrieve the access token 
        access_token = tokens["access"]

        assert not isinstance(response_from_personal_info, list)


        # set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        # Send a POST request to the endpoint
        response = api_client.get(
            f"https://osamaaslam.pythonanywhere.com/resume/get-personal-info-data-for-user/?personal_info_id={response_from_personal_info["id"]}", 
            headers=headers, 
            format="json"
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




@pytest.mark.django_db
class Test_PersonalInfo_for_allowed_methods_in_allow_header:
    """
    tests to check allow http methods , headers in "get-personal-info-data/1/ for OPTIONS request"
    """

    def test_allowed_methods_in_allow_header_for_crud_user(
        self,
        api_client,
        create_access_token_for_user,
        Manually_Verify_Access_Token,
        manually_created_data,
    ):

        # Create the user first! and then get the access token for the created user
        tokens, user = create_access_token_for_user()
        access_token = tokens["access"]

        # set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {access_token}",
        }

        decoded_token = Manually_Verify_Access_Token(access_token)

        user = CustomUser.objects.get(id=decoded_token["user_id"])

        # Add user id to json data
        json_data = manually_created_data

        json_data["user_id"] = user.id
        print(f"json data send to post ------------ :{json_data}")

        response = api_client.post(
            reverse("get-personal-info-data-list"),
            data=json_data,
            headers=headers,
            format="json",
        )

        assert response.status_code == 201

        personal_info_id = response.json()["id"]

        response = api_client.options(
            f"https://osamaaslam.pythonanywhere.com/resume/api/get-personal-info-data/{personal_info_id}/",
            headers=headers,
        )

        # Assert the response status code
        assert response.status_code == status.HTTP_200_OK

        # Assert the allowed methods
        assert (
            "POST" in response.headers["Allow"]
            and "OPTIONS" in response.headers["Allow"]
            and "DELETE" in response.headers["Allow"]
            and "GET" in response.headers["Allow"]
            and "PUT" in response.headers["Allow"]
            and "PATCH" in response.headers["Allow"]
        )
        # for non-CORS
        assert len(response.headers["Allow"].split(", ")) == 6
        # for CORS
        assert len(response.headers["Access-Control-Allow-Methods"].split(", ")) == 6


@pytest.mark.django_db
class Test_PersonalInfo_For_List_Action:
    """
    Test class to test API endpoint ""get-personal-info-data-list", if list and
    action is available
    """

    def test_throttling_settings_for_endpoint1(
        self, create_access_token_for_user, api_client
    ):

        # Create the user first! and then get the access token for the created user
        tokens, user = create_access_token_for_user()
        access_token = tokens["access"]

        # set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {access_token}",
        }

        response = api_client.get(
            reverse("get-personal-info-data-list"),
            headers=headers,
            format="json",
        )
        data = response.json()
        # print(f"daata--------- : {data}")
        assert data == {"detail": 'Method "GET" not allowed.'}
        assert response.status_code == 405


@pytest.mark.django_db
class Test_PersonalInfo_For_Retrieve_Action:
    """
    Test class to test API endpoint ""get-personal-info-data-list", if retrieve
    action is available
    """

    def test_throttling_settings_for_endpoint1(
        self, api_client, create_personal_info_instance_using_api
    ):
        
        # Create PersonalInfo instance by creating a user, and getting the jwt token
        response_from_personal_info , tokens = create_personal_info_instance_using_api()

        access_token = tokens["access"]
        # set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {access_token}",
        }

        id = response_from_personal_info["id"]

        response = api_client.get(
            f"https://osamaaslam.pythonanywhere.com/resume/api/get-personal-info-data/{id}/",
            headers=headers,
            format="json",
        )
        ######  use the if block, when trailing slash is stripped ######
        # if response.status_code == 301:
        #     print(f"Redirected to: {response.url}")
        #     response = api_client.get(response.url, headers=headers, format="json")
        #     # Process the redirected response
        #     print(f"Redirected response: {response.json()}")
        # else:

        assert response.json() is not [] or response.json() is not {}


@pytest.mark.django_db
class Test_PersonalInfo_for_post_request:

    def test_personal_info_for_post_request(
        self,
        api_client,
        create_access_token_for_user,
        create_personal_info_instance_using_api
    ):
        """
        Test the GET method for the endpoint 'get-personal-info-data-for-user'.
        This test checks if the POST request is successful, if the response data matches the expected structure and values,
        and if all expected keys are present in the response data.
        """


        # Create PersonalInfo instance by creating a user, and getting the jwt token
        response_from_personal_info , tokens = create_personal_info_instance_using_api()

        # retrieve the access token 
        access_token = tokens["access"]


        assert not isinstance(response_from_personal_info, list)

        # check number of keys
        assert len(response_from_personal_info) == 22

        # Match the keys with expected keys
        for key in response_from_personal_info:
            assert key in keys_list, f"Missing key: {key}"




@pytest.mark.django_db
class Test_get_personal_info_for_user:

    def test_list_method_for_endpoint_named_get_personal_info_for_user(
        self, api_client, create_personal_info_instance_using_api
    ):
        """
        Test the GET method for the endpoint 'get-personal-info-data-for-user'.
        This test checks if the GET request is successful, if the response data matches the expected structure and values,
        and if all expected keys are present in the response data.

        Returns:
            return a JSON data of all personalinfo instance in list linked to a particular user
        """

        # Create PersonalInfo instance by creating a user, and getting the jwt token
        response_from_personal_info , tokens = create_personal_info_instance_using_api()

        # check the response type
        assert not isinstance(response_from_personal_info, list)
        # check number of keys
        assert len(response_from_personal_info) == 22

        # set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {tokens["access"]}",
        }

        # Retrieve user_id from json response
        user_id = response_from_personal_info["user_id"]

        # Make the GET request
        response = api_client.get(
            f"https://osamaaslam.pythonanywhere.com/resume/get-personal-info-data-for-user/?user_id={user_id}",
            headers=headers,
            format="json",
        )

        # Check if the response status code is 200 (OK)
        assert response.status_code == status.HTTP_200_OK

        # Parse the response JSON
        response_data = response.json()
        print(f"response data---------------: {response_data}")

        # Verify the response data matches the expected structure and values
        assert isinstance(response_data, list)
        assert len(response_data) == 1
        assert response_data[0]["user_id"] == user_id

        for key in response_data[0]:
            assert key in keys_list, f"Missing key: {key}"


@pytest.mark.django_db
class Test_get_personal_info_for_given_personalinfo:

    def test_retrieve_method_for_endpoint_named_get_personal_info_for_personalinfo(
        self, api_client, create_personal_info_instance_using_api
    ):
        """
        Test the GET method for the endpoint 'get-personal-info-data-for-user'.
        This test checks if the GET request is successful, if the response data matches the expected structure and values,
        and if all expected keys are present in the response data.
        Returns:
            return a JSON data of personalinfo instance for particular id for a user in list
        """

        # Create PersonalInfo instance by creating a user, and getting the jwt token
        response_from_personal_info , tokens = create_personal_info_instance_using_api()

        # check the response type
        assert not isinstance(response_from_personal_info, list)
        # check number of keys
        assert len(response_from_personal_info) == 22

        # set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {tokens["access"]}",
        }

        # Retrieve user_id from json response
        user_id = response_from_personal_info["user_id"]
        # Retrieve the PersonalInfo instance id
        id = response_from_personal_info["id"]

        # Make the GET request
        response = api_client.get(
            f"https://osamaaslam.pythonanywhere.com/resume/get-personal-info-data-for-user/?user_id={user_id}&personal_info_id={id}",
            headers=headers,
            format="json",
        )

        # Check if the response status code is 200 (OK)
        assert response.status_code == status.HTTP_200_OK

        # Parse the response JSON
        response_data = response.json()

        # Verify the response data matches the expected structure and values
        assert isinstance(response_data, list)
        assert response_data[0]["user_id"] == user_id

        for key in response_data[0]:
            assert key in keys_list, f"Missing key: {key}"


@pytest.mark.django_db
class Test_patch_personal_info_for_given_personalinfo:

    def test_patch_method_for_endpoint_named_get_personal_info_for_personalinfo(
        self, api_client,  manually_created_data, create_access_token_for_user
    ):
        """
        Test the PATCH method for the endpoint 'get-personal-info-data-for-user'.
        This test checks if the PATCH request is successful, if the response data matches the expected structure and values,
        and if the data from the PATCH request is the same as in the database.
        """

        # Create PersonalInfo instance by creating a user, and getting the jwt token
        response_from_personal_info = manually_created_data
        print(f"response from personal_info------------------------: {response_from_personal_info}")

        tokens, user = create_access_token_for_user()

        # set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {tokens["access"]}",
        }

        response_from_personal_info["user_id"] = user.id

        response = api_client.post(
            reverse("get-personal-info-data-list"),
            data=response_from_personal_info,
            headers=headers,
            format="json",
        )

        assert response.status_code == 201

        # Patch the data
        response_from_personal_info["first_name"] = "named_changed"

        # Get personalinfo instance for user, and retrieve the user's ''first_name' before Patch request is 
        id = response.json()["id"]
        user_id  =response_from_personal_info["user_id"]

        personal_info_instance = PersonalInfo.objects.get(id=id)
        print(f"personal info instance------------ : {personal_info_instance}")


        first_name_before_patch = personal_info_instance.first_name

        # Make the GET request
        response = api_client.patch(
            f"https://osamaaslam.pythonanywhere.com/resume/patch-put-personal-info-data-for-user/?user_id={user_id}&id={id}&partial=True",
            data=response_from_personal_info,
            headers=headers,
            format="json",
        )

        # Check if the response status code is 200 (OK)
        assert response.status_code == 200

        # Parse the response JSON
        response_data = response.json()
        print(f"response after patch request in tests----------- : {response_data}")

        # Verify the response data matches the expected structure and values
        assert not isinstance(response_data, list)  # ==> json
        assert isinstance(response_data, dict)
        assert response_data == {'id': id, 
                                 'user_id': user_id, 
                                 'event': 'cv_updated', 
                                 'status': 'UPDATED', 
                                 'exception': 'None'}  

        # Retrieve the PersonalInfo instance to get 'first_name' after Patch request
        first_name_after_patch = personal_info_instance.first_name
        assert first_name_before_patch != first_name_after_patch


@pytest.mark.django_db
class Test_put_personal_info_for_given_personalinfo:

    def test_put_method_for_endpoint_named_get_personal_info_for_personalinfo(
        self,
        api_client,
        create_personal_info_instance_using_api,
        manually_created_data
    ):
        """
        Test the PUT method for the endpoint 'get-personal-info-data-for-user'.
        This test checks if the PUT request is successful, if the response data matches the expected structure and values,
        and if the data from the PUT request is the same as in the database.
        """

        # Get the JSON for the endpoint according to endpoint Schema
        json_response, tokens = create_personal_info_instance_using_api()

        # print(f"json_response from POST : {json_response}")

        # Retrieve user id and instance id 
        id = json_response["id"]
        user_id = json_response["user_id"]

        # set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {tokens["access"]}",
        }

        # Make the GET request
        manually_created_data["user_id"] = json_response["user_id"]

        response = api_client.put(
            f"https://osamaaslam.pythonanywhere.com/resume/patch-put-personal-info-data-for-user/?user_id={user_id}&id={id}&partial=False",
            data=manually_created_data,
            headers=headers,
            format="json",
        )

        # Check if the response status code is 200 (OK)
        assert response.status_code == status.HTTP_200_OK

        # Parse the response JSON
        response_data = response.json()
        # print(f"data inside put :-----: {response_data}")

        instance = PersonalInfo.objects.get(id=json_response["id"])
        user_id = instance.user_id.id

        # Verify the response data matches the expected structure and values
        assert not isinstance(response_data, list)  # ==> json
        assert response_data == {'id':instance.id, 
                                 'user_id': user_id, 
                                 'event': 'cv_updated', 
                                 'status': 'UPDATED', 
                                 'exception': 'None'}  


@pytest.mark.django_db
class Test_delete_personal_info_instance:
    """
    Test the deletion of a personal info instance.
    """

    def test_delete_personal_info(self, api_client, create_personal_info_instance_using_api):
        """
        This test checks if a personal info instance can be successfully deleted
        using the API.
        """

        # Get the JSON for the endpoint according to endpoint Schema
        json_response, tokens = create_personal_info_instance_using_api()

        print(f"json_response from POST : {json_response}")

        # Retrieve user id and instance id 
        id = json_response["id"]
        user_id = json_response["user_id"]

        # Verify PersonalInfo exist in database
        assert PersonalInfo.objects.filter(id=id).exists() == True

        # set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {tokens["access"]}",
        }
        # Get the URL for the delete endpoint
        url = f"https://osamaaslam.pythonanywhere.com/resume/api/get-personal-info-data/{id}/"

        # Make the DELETE request
        response = api_client.delete(url, headers=headers)

        # Check if the request was successful (HTTP 204 No Content)
        assert response.status_code == 204

        # Check if the PersonalInfo object is actually deleted from the database
        assert not PersonalInfo.objects.filter(id=id).exists()


@pytest.mark.django_db
class Test_Webhook_PostPersonalInfoInstance:
    def test_personal_info_for_webhook_event_for_post_request(
        self,
        api_client,
        create_access_token_for_user,
        personal_info_data,
    ):
        """
        Test the webhook event for a POST request to the personal info endpoint.
        This function creates a user, generates personal info data, makes a POST request to the endpoint,
        and mocks the webhook URL. It then checks if the webhook was called with the expected data.
        """

        # Create User, and Get the access token for this created user
        tokens, user = create_access_token_for_user()

        # Get the JSON for the endpoint according to endpoint Schema
        json_data, personal_info_instance, user = personal_info_data(user)

        # Create user
        json_data["user_id"] = user.id

        # Set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {tokens["access"]}",
        }

        # Mock the webhook URL
        webhook_url = "https://osama11111.pythonanywhere.com/cv-webhook/"
        with requests_mock.Mocker() as m:
            m.post(webhook_url, status_code=200)

            response = api_client.post(
                reverse("get-personal-info-data-list"),
                data=json_data,
                headers=headers,
                format="json",
            )

            print(f"post_response-----------------{response.json()}")
            assert m.called
            assert m.call_count == 1
            request = m.request_history[0]
            assert request.url == webhook_url

            personal_info_instance = PersonalInfo.objects.get(user_id=user.id)

            assert request.json()["id"] == personal_info_instance.id
            assert request.json()["user_id"] == user.id
            assert request.json()["event"] == "cv_created"



@pytest.mark.django_db
class Test_Webhook_DeletePersonalInfoInstance:

    def test_webhook_event_for_delete_request_to_personal_info(
        self, api_client, create_personal_info_instance_using_api
    ):
        """
        Test the webhook event for a DELETE request to the personal info.
        This function mocks the webhook URL, makes a DELETE request to delete the personal info,
        and checks if the webhook was called with the expected data.
        """
        
        # Create User, and Get the access token for this created user
        json_response, tokens = create_personal_info_instance_using_api()

        # Retrieve user id and instance id 
        id = json_response["id"]
        user_id = json_response["user_id"]

        # Verify PersonalInfo exist in database
        assert PersonalInfo.objects.filter(id=id).exists() == True

        # Set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {tokens["access"]}",
        }

        # Mock the webhook URL for delete
        webhook_url = "https://osama11111.pythonanywhere.com/cv-webhook/"
        with requests_mock.Mocker() as m:
            m.post(webhook_url, status_code=200)

            # Make the DELETE request
            delete_response = api_client.delete(reverse(
                "get-personal-info-data-detail", args=[id]),
                headers=headers,
            )
            assert delete_response.status_code == 204

            # Confirm if object is deleted
            assert not PersonalInfo.objects.filter(id=id).exists()

            # Check if the webhook was called
            assert m.called
            assert m.call_count == 1
            request = m.request_history[0]
            assert request.url == webhook_url
            assert request.json() == {
                "event": "cv_deleted",
                "id": id,
                "user_id": user_id,
            }


@pytest.mark.django_db
class Test_Webhook_PatchPersonalInfoInstance:

    def test_webhook_event_for_delete_request_to_personal_info(
        self, api_client, create_personal_info_instance_using_api, fetching_data_from_database_and_create_JSON
    ):
        """
        Test to check if signal is triggered for a PATCH request to the personal info.
        """
        # Create User, and Get the access token for this created user
        json_response, tokens = create_personal_info_instance_using_api()
        # print(f"json response from POST in tests class--------: {json_response}")


        # Retrieve user id and instance id 
        id = json_response["id"]
        user_id = json_response["user_id"]

        # Verify PersonalInfo exist in database
        assert PersonalInfo.objects.filter(id=id).exists() == True

        # json data to be sent
        json_data = fetching_data_from_database_and_create_JSON(id)
        json_data["user_id"] = user_id
        # print(f"fetch data and create JSON tests class--------: {json_response}")

        # Set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {tokens["access"]}",
        }


        json_data["first_name"] = "first name changed"
        # Mock the webhook URL
        webhook_url = "https://osama11111.pythonanywhere.com/cv-webhook/"

        with requests_mock.Mocker() as n:
            n.post(webhook_url, status_code=200)

            # Make the POST request
            response = api_client.patch(
                f"https://osamaaslam.pythonanywhere.com/resume/patch-put-personal-info-data-for-user/?user_id={user_id}&id={id}&partial=True",
                data=json_data,
                headers=headers,
                format="json",
            )
            # Assertions
            print(f"error--------------: {response.json()}")
            assert response.status_code == 200

            # Check if the webhook was called
            assert not n.called
        #     assert n.call_count == 1
        #     request_1 = n.request_history[0]

        #     # request_2 = n.request_history[1]
        #     assert request_1.url == webhook_url

        #     assert request_1.json() == {
        #     "id": id,
        #     "user_id": user_id,
        #     "event": "cv_created",
        #     "status": "CREATED",
        #     "exception": str("None"),
        # }
        

@pytest.mark.django_db
class Test_Webhook_PatchPersonalInfoInstance:

    def test_webhook_event_for_delete_request_to_personal_info(
        self, api_client, create_personal_info_instance_using_api, fetching_data_from_database_and_create_JSON
    ):
        """
        Test the signal event for a PATCH request to the personal info.
        and checks if the webhook is called or not.
        """
        # Create User, and Get the access token for this created user
        json_response, tokens = create_personal_info_instance_using_api()
        # print(f"json response from POST in tests class--------: {json_response}")


        # Retrieve user id and instance id 
        id = json_response["id"]
        user_id = json_response["user_id"]

        # Verify PersonalInfo exist in database
        assert PersonalInfo.objects.filter(id=id).exists() == True

        # json data to be sent
        json_data = fetching_data_from_database_and_create_JSON(id)
        json_data["user_id"] = user_id
        # print(f"fetch data and create JSON tests class--------: {json_response}")

        # Set the access token in headers
        headers = {
            "Origin": "https://web.postman.co",
            "Authorization": f"Bearer {tokens["access"]}",
        }


        json_data["first_name"] = "first name changed"
        # Mock the webhook URL
        webhook_url = "https://osama11111.pythonanywhere.com/cv-webhook/"

        with requests_mock.Mocker() as n:
            n.post(webhook_url, status_code=200)

            # Make the POST request
            response = api_client.put(
                f"https://osamaaslam.pythonanywhere.com/resume/patch-put-personal-info-data-for-user/?user_id={user_id}&id={id}&partial=True",
                data=json_data,
                headers=headers,
                format="json",
            )
            # Assertions
            print(f"error--------------: {response.json()}")
            assert response.status_code == 200

            # Check if the webhook was called
            assert not n.called
        #     assert n.call_count == 1
        #     request_1 = n.request_history[0]

        #     # request_2 = n.request_history[1]
        #     assert request_1.url == webhook_url

        #     assert request_1.json() == {
        #     "id": id,
        #     "user_id": user_id,
        #     "event": "cv_created",
        #     "status": "CREATED",
        #     "exception": str("None"),
        # }

