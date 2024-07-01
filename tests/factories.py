# your_app/tests/factories.py
import factory
from api_auth.models import CustomUser
from faker import Faker
from resume.models import (
    PersonalInfo,
    Overview,
    Education,
    Job,
    SkillAndSkillLevel,
    ProgrammingArea,
    Projects,
    Publication,
    JobAccomplishment,
)
from random import choice


# Function to create a user and return user details
def create_user_details(
    username="testuser11",
    email="testuser11@example.com",
    password="testpass123",
):
    user = UserFactory(username=username, email=email)
    user.set_password(password)
    user.save()
    return {
        "username": user.username,
        "email": user.email,
        "password": password,
        "test_user": user,
    }


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class UserFactory_Seializer_Testing(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_staff = factory.Faker("boolean", chance_of_getting_true=100)
    is_active = factory.Faker("boolean", chance_of_getting_true=100)


class PersonalInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PersonalInfo

    user_id = factory.SubFactory(UserFactory)
    first_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    suffix = factory.Faker("suffix")
    locality = factory.Faker("city")
    region = factory.Faker("state")
    title = factory.Faker("job")
    email = factory.Faker("email")
    linkedin = factory.Faker("url")
    facebook = factory.Faker("url")
    github = factory.Faker("url")
    site = factory.Faker("url")
    twittername = factory.Faker("user_name")


class OverviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Overview

    personal_info = factory.SubFactory(PersonalInfoFactory)
    text = factory.Faker("text")


class EducationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Education

    personal_info = factory.SubFactory(PersonalInfoFactory)
    name = factory.Faker("word")
    location = factory.Faker("city")
    schoolurl = factory.Faker("url")
    education_start_date = factory.Faker("date")
    education_end_date = factory.Faker("date")
    degree = factory.Faker("word")
    description = factory.Faker("paragraph")


class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job

    personal_info_job = factory.SubFactory(PersonalInfoFactory)
    company = factory.Faker("company")
    companyurl = factory.Faker("url")
    location = factory.Faker("city")
    title = factory.Faker("job")
    description = factory.Faker("paragraph")
    job_start_date = factory.Faker("date")
    job_end_date = factory.Faker("date")
    is_current = factory.Faker("boolean")
    is_public = factory.Faker("boolean")
    image = ""  # Setting the image field to an empty string          ==> null= False, blank=True
    # image = None  # Setting the image field to None to keep it empty ==> null=True, blank=True
    # image = factory.django.ImageField()


class JobAccomplishmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JobAccomplishment

    job = factory.SubFactory(JobFactory)
    job_accomplishment = factory.Faker("paragraph")


class SkillAndSkillLevelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SkillAndSkillLevel

    personal_info = factory.SubFactory(PersonalInfoFactory)
    text = factory.Faker("word")
    skill_level = factory.Faker(
        "random_element",
        elements=[choice[0] for choice in SkillAndSkillLevel.SKILL_LEVEL_CHOICES],
    )


class ProgrammingAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProgrammingArea

    personal_info = factory.SubFactory(PersonalInfoFactory)
    programming_area_name = factory.Faker(
        "random_element", elements=["FRONTEND", "BACKEND"]
    )

    @factory.lazy_attribute
    def programming_language_name(self):
        if self.programming_area_name == "FRONTEND":
            return choice(ProgrammingArea.FRONTEND_PROGRAMMING_LANGUAGE_CHOICES)[0]
        else:
            return choice(ProgrammingArea.BACKEND_PROGRAMMING_LANGUAGE_CHOICES)[0]


class ProjectsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Projects

    personal_info = factory.SubFactory(PersonalInfoFactory)
    project_name = factory.Faker("word")
    short_description = factory.Faker("paragraph")
    long_description = factory.Faker("paragraph")
    link = factory.Faker("url")


class PublicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Publication

    personal_info = factory.SubFactory(PersonalInfoFactory)
    title = factory.Faker("sentence")
    authors = factory.Faker("name")
    journal = factory.Faker("word")
    year = factory.Faker("year")
    link = factory.Faker("url")
