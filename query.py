import factory
from factory.django import DjangoModelFactory
from resume.models import CustomUser, PersonalInfo, Job, JobAccomplishment
from django.core.management.base import BaseCommand
from faker import Faker
from termcolor import (
    colored,
)


# Faker instance for generating fake data
fake = Faker()


# Define model factories using factory_boy
class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class PersonalInfoFactory(DjangoModelFactory):
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


# Define a Django management command
class Command(BaseCommand):
    help = "Query PersonalInfo with related Job and JobAccomplishment"

    def handle(self, *args, **kwargs):
        # Create test data
        # Create 3 users
        users = UserFactory.create_batch(3)

        # Create 3 PersonalInfo instances for each user
        for user in users:
            for _ in range(3):
                personal_info = PersonalInfoFactory(user_id=user)
                job = JobFactory(personal_info_job=personal_info)
                JobAccomplishmentFactory(job=job)

        # Query PersonalInfo with related Job and JobAccomplishment
        personal_info_with_jobs = PersonalInfo.objects.select_related(
            "job", "job__jobaccomplishment"
        ).all()

        # Print the details in a more colorful and structured way
        for pi in personal_info_with_jobs:
            self.stdout.write(
                colored(f"User: {pi.full_name()}", "cyan", attrs=["bold"])
            )
            job = pi.job
            if job:
                self.stdout.write(
                    colored(f"  Job: {job.company}, Title: {job.title}", "yellow")
                )
                job_accomplishment = job.jobaccomplishment
                if job_accomplishment:
                    self.stdout.write(
                        colored(
                            f"    Accomplishment: {job_accomplishment.job_accomplishment}",
                            "green",
                        )
                    )
                else:
                    self.stdout.write(colored("    No accomplishments found", "red"))
            else:
                self.stdout.write(colored("  No job information found", "red"))

            self.stdout.write("")
