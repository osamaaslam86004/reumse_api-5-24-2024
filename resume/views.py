from resume.models import PersonalInfo
from resume.forms import (
    PersonalInfoForm,
    OverviewForm,
    EducationfoForm,
    JobfoForm,
    JobAccomplishmentfoForm,
    ProjectsForm,
    ProgrammingAreaForm,
    PublicationForm,
    SkillAndSkillLevelForm,
)
from resume.resume_pagination import LargeResultsSetPagination
from resume.serializers import PersonalInfo_Serializer
from django.http import (
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    JsonResponse,
)
from formtools.wizard.views import SessionWizardView
import json, requests
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.cache import cache_control

# from rest_framework.decorators import action
from django.db import transaction
from api_auth.models import CustomUser
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views import View
from django.contrib import messages
from django.conf import settings
from resume_api.custom_user_rated_throtle_class import CustomUserRateThrottle


class Homepage(View):
    def get(self, request, **kwargs):
        if not settings.DEBUG:
            return HttpResponseRedirect(
                "https://osamaaslam.pythonanywhere.com/api/schema/swagger-ui/"
            )
        else:
            return HttpResponseRedirect(
                "https://diverse-intense-whippet.ngrok-free.app/api/schema/swagger-ui/"
            )


def condition_callable(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step("0") or {}
    condition_value = cleaned_data.get("condition")
    return condition_value == "True"


class PersonalInfoWizard(SessionWizardView):
    form_list = [
        PersonalInfoForm,
        PublicationForm,
        OverviewForm,
        EducationfoForm,
        JobfoForm,
        JobAccomplishmentfoForm,
        SkillAndSkillLevelForm,
        ProgrammingAreaForm,
        ProjectsForm,
    ]
    template_name = "wizard_view.html"
    condition_dict = {"1": condition_callable}

    def done(self, form_list, **kwargs):
        condition = form_list[0].cleaned_data["condition"]
        personal_info_form = form_list[0]
        PersonalInfo = personal_info_form.save(commit=False)

        try:
            id_user = self.request.GET.get("user_id")
            user = CustomUser.objects.filter(id=id_user).first()
            if user:
                print(f"user________{user}")
        except Exception as e:
            return JsonResponse({"error": str(e)})

        if condition == "False":
            over_view = form_list[1]
            education_data = form_list[2]
            job_data = form_list[3]
            job_accomplishment_data = form_list[4]
            skill_and_skill_level_data = form_list[5]
            programming_area_data = form_list[6]
            projects_data = form_list[7]

            overview = over_view.save(commit=False)
            education = education_data.save(commit=False)
            job = job_data.save(commit=False)
            accomplishment = job_accomplishment_data.save(commit=False)
            skill = skill_and_skill_level_data.save(commit=False)
            programming_area = programming_area_data.save(commit=False)
            projects = projects_data.save(commit=False)

            PersonalInfo.user_id = user
            PersonalInfo.save()

            overview.personal_info = PersonalInfo
            overview.save()
            education.personal_info = PersonalInfo
            education.save()
            job.personal_info_job = PersonalInfo
            job.save()
            accomplishment.job = job
            accomplishment.save()
            skill.personal_info = PersonalInfo
            skill.save()
            programming_area.personal_info = PersonalInfo
            programming_area.save()
            projects.personal_info = PersonalInfo
            projects.save()

            messages.success(self.request, "CV created successfully!")
            if settings.DEBUG:
                return HttpResponsePermanentRedirect(
                    "https://diverse-intense-whippet.ngrok-free.app/"
                )
            else:
                return HttpResponsePermanentRedirect(
                    "https://osama11111.pythonanywhere.com/"
                )

        else:
            PersonalInfo = form_list[0]
            del PersonalInfo.cleaned_data["condition"]
            PersonalInfo.save(commit=False)

            publication_data = form_list[2]
            over_view = form_list[3]
            education_data = form_list[4]
            job_data = form_list[5]
            job_accomplishment_data = form_list[6]
            skill_and_skill_level_data = form_list[7]
            programming_area_data = form_list[8]
            projects_data = form_list[9]

            publication = publication_data.save(commit=False)
            overview = over_view.save(commit=False)
            education = education_data.save(commit=False)
            job = job_data.save(commit=False)
            accomplishment = job_accomplishment_data.save(commit=False)
            skill = skill_and_skill_level_data.save(commit=False)
            programming_area = programming_area_data.save(commit=False)
            projects = projects_data.save(commit=False)

            PersonalInfo.user_id = user
            PersonalInfo.save()

            publication.personal_info = PersonalInfo
            publication.save()
            overview.personal_info = PersonalInfo
            overview.save()
            education.personal_info = PersonalInfo
            education.save()
            job.personal_info_job = PersonalInfo
            job.save()
            accomplishment.job = job
            accomplishment.save()
            skill.personal_info = PersonalInfo
            skill.save()
            programming_area.personal_info = PersonalInfo
            programming_area.save()
            projects.personal_info = PersonalInfo
            projects.save()

            messages.success(self.request, "CV created successfully!")
            if settings.DEBUG:
                return HttpResponsePermanentRedirect(
                    "https://diverse-intense-whippet.ngrok-free.app/"
                )
            else:
                return HttpResponsePermanentRedirect(
                    "https://osama11111.pythonanywhere.com/"
                )


@method_decorator(cache_control(private=True), name="dispatch")
@method_decorator(cache_page(60 * 60 * 2), name="dispatch")
@method_decorator(vary_on_headers("User-Agent"), name="dispatch")
class PersonalInfo_List_CreateView(viewsets.ModelViewSet):
    queryset = PersonalInfo.objects.order_by("-id")
    lookup_field = "id"
    serializer_class = PersonalInfo_Serializer
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    authentication_classes = [JWTStatelessUserAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomUserRateThrottle]
    pagination_classes = LargeResultsSetPagination
    http_method_names = ["post", "delete", "get", "put", "patch", "options"]
    allowed_methods = ["POST", "GET", "OPTIONS", "PUT", "PATCH", "DELETE"]

    def add_throttle_headers(self, request, response):
        response["X-RateLimit-Limit"] = request.rate_limit["X-RateLimit-Limit"]
        response["X-RateLimit-Remaining"] = request.rate_limit["X-RateLimit-Remaining"]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self.add_throttle_headers(request, response)
        return response

    def perform_update(self, serializer):
        # this is not django request, instead a django rest framework request: both are different
        # print(f"self.request : {self.request}")

        # Doing commit = False for serializer to get model instance
        # ==> model_instance = form.save(commit=False)
        instance = serializer.instance
        user_id = None
        id = None

        if instance.user_id:
            user_id = instance.user_id.id
        else:
            personal_info_instance = PersonalInfo.objects.filter(id=instance.id).first()
            if personal_info_instance:
                user_id = personal_info_instance.user_id.id

        if instance:
            id = instance.id

        # print(f"user_id : {user_id} and id in self.perfom update------------: {id}")

        try:
            with transaction.atomic():
                try:
                    response = super().perform_update(serializer)
                except Exception as e:
                    raise Exception({"detail super()": str(e)})

                if user_id:
                    transaction.on_commit(
                        lambda: (
                            self.send_notification(
                                event="cv_updated",
                                status_="UPDATED",
                                exception=None,
                                user_id=user_id,
                                id=id,
                                request=self.request,
                            )
                        )
                    )
                else:
                    transaction.on_commit(
                        lambda: (
                            self.send_notification(
                                event="cv_updated",
                                status_="UPDATED",
                                id=id,
                                exception=None,
                                user_id=None,
                                request=self.request,
                            )
                        )
                    )
        except Exception as e:
            self.send_notification(
                event="cv_update_fail",
                exception=str(e),
                status_="FAILED",
                user_id=user_id if user_id else None,
                id=id,
                request=self.request,
            )
            raise Exception(e)

    def destroy(self, request, *args, **kwargs):
        personal_info_id = kwargs["id"]
        personal_info = PersonalInfo.objects.filter(id=personal_info_id)
        print(f"personal_info_id__________delete___{personal_info}")

        if personal_info:

            try:
                with transaction.atomic():
                    self.perform_destroy(personal_info[0])
                    print("perform deleted is perfomed")

                    # Do not use HTTP_204_NO_CONTENT, it is not equivalent to HTTP 204 DELETE
                    # HTTP_204_NO_CONTENT  => Means Content / PersonalInfo Object Not Found

                    response = Response(
                        {"success": "CV deleted successfully"},
                        status=status.HTTP_204_NO_CONTENT,
                    )

            except Exception as e:
                response = Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            response = Response(
                {"error": "Personal Info does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.add_throttle_headers(request, response)
        return response

    def get_personal_info_for_user(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        personal_info_id = request.query_params.get("personal_info_id")

        filter_kwargs = {}
        try:
            if personal_info_id:
                queryset = self.get_queryset().filter(
                    id=personal_info_id, user_id=user_id
                )
                filter_kwargs = {"user_id": user_id, "id": personal_info_id}
            else:
                queryset = self.get_queryset().filter(user_id=user_id)
                filter_kwargs = {
                    "user_id": user_id,
                }
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)

        except Exception as e:
            response = JsonResponse({"error": str(e)})

        self.add_throttle_headers(request, response)
        return response

    def patch_personal_info_for_user(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        id = request.query_params.get("id")

        # print(f"user id------ : {user_id} : id-----: {id}")

        # check for user id is not none and id is not empty
        if user_id is not None and id is not None:
            # Check if partial is available as **kwargs
            if "partial" in kwargs:
                partial = True if kwargs.pop("partial").lower() == "true" else False

            elif "partial" in request.query_params:
                # Check if partial is available as query parameter
                partial = (
                    True
                    if request.query_params.get("partial").lower() == "true"
                    else False
                )
            else:
                response = Response(
                    {"error": " 'partial' is not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                self.add_throttle_headers(request, response)
                return response
        else:
            response = Response(
                {"error": "'user_id' or 'id' is not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            self.add_throttle_headers(request, response)
            return response

        # print(f"partial-------------- : {partial}")
        instance = PersonalInfo.objects.filter(user_id__id=user_id, id=id).first()
        # print(f"instance-------: {instance}")

        if not instance:
            response = Response(
                {"error": "Personal Info does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            self.add_throttle_headers(request, response)
            return response

        if user_id not in request.data:
            request.data["user_id"] = user_id
        # want to pass/access variables / keys / query parameters from ModelSets method to/within
        # crete(), update() method of Serializer class, then pass these in context dictionary

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={"user_id": user_id, "id": id},
        )

        serializer.is_valid(raise_exception=True)
        print(f"serializer_data.validated_data : {serializer.validated_data}")

        try:
            self.perform_update(serializer)
            response = Response(
                data={
                    "id": int(id),
                    "user_id": int(user_id),
                    "event": "cv_updated",
                    "status": "UPDATED",
                    "exception": "None",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            response = Response(
                {"exception in self.perfom_update()----------------": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        self.add_throttle_headers(request, response)
        return response

    def send_notification(self, event, **kwargs):
        request = kwargs.get("request", None)

        if not settings.DEBUG:
            WEBHOOK_URL = "https://osama11111.pythonanywhere.com/cv-webhook/"
        else:
            WEBHOOK_URL = "https://diverse-intense-whippet.ngrok-free.app/cv-webhook/"

        # Convert header values to strings
        headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": str(request.rate_limit["X-RateLimit-Limit"]),
            "X-RateLimit-Remaining": str(request.rate_limit["X-RateLimit-Remaining"]),
        }
        # print(f"event named in send_webhook: ------------: {event}")
        # print(f"headers in send_webhook: ------------: {headers}")

        if event in ["cv_updated", "cv_update_fail"]:
            user_id = kwargs.get("user_id", None)
            id = kwargs.get("id")

            data = {
                "id": id,
                "user_id": user_id,
                "event": event,
                "status": kwargs.get("status_", "UNKNOWN"),
                "exception": kwargs.get("exception", "None"),
            }

            data = json.dumps(data)

        try:
            response = requests.post(WEBHOOK_URL, headers=headers, data=data)
            response.raise_for_status()

        except requests.RequestException as e:
            print(f"Failed to send webhook: {str(e)}")
            pass

    def list(self, request, *args, **kwargs):
        response = Response(
            {"detail": 'Method "GET" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        response["Content-Type"] = "application/json"
        return response

    def update(self, request, *args, **kwargs):
        response = Response(
            {"detail": 'Method "PUT" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        response["Content-Type"] = "application/json"
        return response

    def partial_update(self, request, *args, **kwargs):
        response = Response(
            {"detail": 'Method "PATCH" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        response["Content-Type"] = "application/json"
        return response


# from django.core.files.storage import FileSystemStorage
# from formtools.preview import FormPreview
# from resume.forms import PersonalInfoForm, PublicationForm, OverviewForm


# class PersonalInfoPreviewWizard(FormPreview):
#     form_template = "wizard_view_form.html"
#     preview_template = "preview_wizard.html"

#     def done(self, request, cleaned_data):
#         print(cleaned_data)
#         del cleaned_data["condition"]
#         print(cleaned_data)
#         info_instance = PersonalInfo.objects.create(**cleaned_data)
#         return HttpResponseRedirect("/page-to-redirect-to-when-done/")


# def list(self, request, *args, **kwargs):
#     response = Response(
#         {"detail": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
#     )
#     self.add_throttle_headers(request, response)
#     return response

# def retrieve(self, request, *args, **kwargs):
#     response = Response(
#         {"detail": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
#     )
#     self.add_throttle_headers(request, response)
#     return response
