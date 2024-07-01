import factory
from factory.django import DjangoModelFactory
from resume.models import CustomUser, PersonalInfo, Job, JobAccomplishment
from django.core.management.base import BaseCommand


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


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


class JobFactory(DjangoModelFactory):
    class Meta:
        model = Job

    personal_info_job = factory.SubFactory(PersonalInfoFactory)
    company = factory.Faker("company")
    title = factory.Faker("job")
    job_start_date = factory.Faker("date")
    job_end_date = factory.Faker("date")


class JobAccomplishmentFactory(DjangoModelFactory):
    class Meta:
        model = JobAccomplishment

    job = factory.SubFactory(JobFactory)
    job_accomplishment = factory.Faker("sentence")


class Command(BaseCommand):
    help = "Query PersonalInfo with related Job and JobAccomplishment"

    def handle(self, *args, **kwargs):

        # Create test data
        personal_info = PersonalInfoFactory()
        job = JobFactory(personal_info_job=personal_info)
        JobAccomplishmentFactory(job=job)

        # Query PersonalInfo with related Job and JobAccomplishment
        personal_info_with_jobs = PersonalInfo.objects.select_related(
            "job", "job__accomplishment"
        ).all()
        for pi in personal_info_with_jobs:
            self.stdout.write(f"User: {pi.full_name()}")
            job = pi.job
            if job:
                self.stdout.write(f"  Job: {job.company}, Title: {job.title}")
                if job.accomplishment:
                    self.stdout.write(
                        f"    Accomplishment: {job.accomplishment.job_accomplishment}"
                    )
