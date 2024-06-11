# # create_usertoken.py

# from django.core.management.base import BaseCommand
# from django.contrib.auth import get_user_model
# from rest_framework_simplejwt.tokens import AccessToken
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework_simplejwt.tokens import Token


# class Command(BaseCommand):
#     help = "Create a user, generate an access token, print it, and store it as a string"

#     def handle(self, *args, **kwargs):
#         User = get_user_model()

#         # Create or get the user
#         user, _ = User.objects.get_or_create(
#             username="accesstoken", email="email@gmail.com", password="password"
#         )

#         # Generate an access token for the user
#         access_token_1 = AccessToken.for_user(user)

#         # Print the access token in the terminal
#         self.stdout.write(f"Access Token for User '{user.username}' : {access_token_1}")

#         access_token_2 = AccessToken.for_user(user)

#         # Print the access token in the terminal
#         self.stdout.write(f"Access Token for User '{user.username}' : {access_token_2}")

#         if access_token_2 == access_token_1:
#             self.stdout.write("Access are same")
#         else:
#             self.stdout.write("Access are diffrent")

#         user = JWTAuthentication().get_user(access_token_2)
#         self.stdout.write(f"user name : {user.username} : email {user.email}")


# from django.core.management.base import BaseCommand
# from tests.factories import ProgrammingAreaFactory
# from resume.serializers import ProgrammingAreaSerializer


# class Command(BaseCommand):
#     help = "Generate data using ProgrammingAreaFactory and save using ProgrammingAreaSerializer"

#     def handle(self, *args, **options):
#         # Step 1: Generate data using ProgrammingAreaFactory
#         data = ProgrammingAreaFactory.create_batch(1)  # Create a batch of one instance

#         # Step 2: Print out explicitly defined attributes of the factory class and their values
#         self.stdout.write(
#             "Attributes and values of generated ProgrammingAreaFactory instance(s):"
#         )
#         for instance in data:
#             self.stdout.write(f"Instance ID: {instance.id}")
#             self.stdout.write(f"personal_info: {instance.personal_info}")
#             self.stdout.write(
#                 f"programming_area_name: {instance.programming_area_name}"
#             )
#             self.stdout.write(
#                 f"programming_language_name: {instance.programming_language_name}"
#             )

#         # Step 3: Use ProgrammingAreaSerializer to save the data
#         serializer = ProgrammingAreaSerializer(
#             data=[
#                 {
#                     "programming_area_name": instance.programming_area_name,
#                     "programming_language_name": instance.programming_language_name,
#                 }
#                 for instance in data
#             ],
#             many=True,
#         )
#         if serializer.is_valid():
#             serializer.save()
#             self.stdout.write("Data saved successfully.")
#         else:
#             self.stdout.write(f"Error: Invalid data. {serializer.errors}")

#         self.stdout.write(self.style.SUCCESS("Successfully generated and saved data."))


# Inside generate_data.py

# from django.core.management.base import BaseCommand
# from api_auth.tests.factories import SkillAndSkillLevelFactory
# from resume.serializers import SkillAndSkillLevelSerializer


# class Command(BaseCommand):
#     help = "Generate data using SkillAndSkillLevelFactory and save using SkillAndSkillLevelSerializer"

#     def handle(self, *args, **options):
#         # Step 1: Generate data using SkillAndSkillLevelFactory
#         data = SkillAndSkillLevelFactory.create_batch(1)

#         # Step 2: Print out explicitly defined attributes of the factory class and their values
#         self.stdout.write(
#             "Attributes and values of generated SkillAndSkillLevelFactory instance(s):"
#         )
#         for instance in data:
#             self.stdout.write(f"Instance ID: {instance.id}")
#             self.stdout.write(f"personal_info: {instance.personal_info}")
#             self.stdout.write(f"text: {instance.text}")
#             self.stdout.write(f"skill_level: {instance.skill_level}")

#         # Step 3: Use SkillAndSkillLevelSerializer to save the data
#         serializer = SkillAndSkillLevelSerializer(
#             data=[
#                 {
#                     "personal_info": instance.personal_info.id,
#                     "text": instance.text,
#                     "skill_level": instance.skill_level,
#                 }
#                 for instance in data
#             ],
#             many=True,
#         )
#         if serializer.is_valid():
#             serializer.save()
#             self.stdout.write("Data saved successfully.")
#         else:
#             self.stdout.write(f"Error: Invalid data. {serializer.errors}")

#         self.stdout.write(self.style.SUCCESS("Successfully generated and saved data."))


# from django.core.management.base import BaseCommand
# from api_auth.tests.factories import EducationFactory, JobFactory
# class Command(BaseCommand):
#     help = "Print instances of Education and Job classes"

#     def handle(self, *args, **options):
#         # Print instances of Education
#         self.stdout.write("Education instances:\n")
#         for education_instance in EducationFactory.create_batch(
#             1
#         ):  # Adjust batch size as needed
#             self.stdout.write("Education instance:")
#             self.stdout.write(f"Name: {education_instance.name}")
#             self.stdout.write(f"Location: {education_instance.location}")
#             self.stdout.write(f"School URL: {education_instance.schoolurl}")
#             self.stdout.write(
#                 f"Education start date: {education_instance.education_start_date}"
#             )
#             self.stdout.write(
#                 f"Education end date: {education_instance.education_end_date}"
#             )
#             self.stdout.write(f"Degree: {education_instance.degree}")
#             self.stdout.write(f"Description: {education_instance.description}")
#             self.stdout.write("\n")

#         # Print instances of Job
#         self.stdout.write("\nJob instances:\n")
#         for job_instance in JobFactory.create_batch(1):  # Adjust batch size as needed
#             self.stdout.write("Job instance:")
#             self.stdout.write(f"Company: {job_instance.company}")
#             self.stdout.write(f"Company URL: {job_instance.companyurl}")
#             self.stdout.write(f"Location: {job_instance.location}")
#             self.stdout.write(f"Title: {job_instance.title}")
#             self.stdout.write(f"Description: {job_instance.description}")
#             self.stdout.write(f"Job start date: {job_instance.job_start_date}")
#             self.stdout.write(f"Job end date: {job_instance.job_end_date}")
#             self.stdout.write(f"Is current: {job_instance.is_current}")
#             self.stdout.write(f"Is public: {job_instance.is_public}")
#             self.stdout.write(f"Image: {job_instance.image}")
#             self.stdout.write("\n")
