from django.shortcuts import render, get_object_or_404
from resume.models import (
    PersonalInfo,
    Overview,
    Education,
    Job,
    JobAccomplishment,
    Projects,
    ProgrammingArea,
    Publication,
    SkillAndSkillLevel,
)
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
from resume.serializers import (
    PersonalInfo_Serializer,
    OverviewSerializer,
    EducationListCreateSerializer,
    ProjectsSerializer,
    SkillAndSkillLevelSerializer,
    ProgrammingAreaSerializer,
    PersonalInfo__Serializer
)
from django.http import HttpResponseRedirect
from formtools.wizard.views import SessionWizardView
import json, requests
from django.urls import reverse_lazy
from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets, status
from resume.serializers import PersonalInfo_Serializer
from rest_framework.response import Response
from rest_framework.decorators import action
from functools import partial
from django.db import transaction
from api_auth.models import CustomUser
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views import View
 


class Homepage(View):
    def get(self, request, **kwargs):
        return HttpResponseRedirect('https://resume-api-pink.vercel.app/api/schema/redoc/')






class PersonalInfoViewSet(viewsets.ModelViewSet):
    queryset = PersonalInfo.objects.order_by("-id")
    serializer_class = PersonalInfo__Serializer
    lookup_field = "id"
    pagination_class = LargeResultsSetPagination


class OverviewViewSet(viewsets.ModelViewSet):
    queryset = Overview.objects.order_by("-id")
    serializer_class = OverviewSerializer
    lookup_field = "id"


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.order_by("-id")
    serializer_class = EducationListCreateSerializer
    lookup_field = "id"
    pagination_class = LargeResultsSetPagination



class SkillViewSet(viewsets.ModelViewSet):
    queryset = SkillAndSkillLevel.objects.order_by("-id")
    serializer_class = SkillAndSkillLevelSerializer
    lookup_field = "id"
    pagination_class = LargeResultsSetPagination


class ProgrammingAreaViewSet(viewsets.ModelViewSet):
    queryset = ProgrammingArea.objects.order_by("-id")
    serializer_class = ProgrammingAreaSerializer
    lookup_field = "id"


class ProjectsViewSet(viewsets.ModelViewSet):
    queryset = Projects.objects.order_by("-id")
    serializer_class = ProjectsSerializer
    lookup_field = "id"
    pagination_class = LargeResultsSetPagination




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
    # file_storage = FileSystemStorage(location="/tmp")

    def done(self, form_list, **kwargs):
        condition = form_list[0].cleaned_data["condition"]
        PersonalInfo = form_list[0].save(commit=False)
         
        try:
            # [user_id is explicitly written in url] get any query parameter from url  => ?=user_id=1 if url does not contain <int:user_id> in url_pattrens urls.py
            # [user_id is implicitly written in url] equivalent to https:url.com/1/    => if url in urls.py contains <int:user_id>
            #  
            id_user= self.request.GET.get('user_id')

            print(f"kwargs______{id_user}")

            user = CustomUser.objects.filter(id = id_user)
            if user:
                user = user[0]
                print(f"user________{user}")
        except Exception as e:
            return JsonResponse({"error" : str(e)})

        if condition == "False":
            # Learning Point = we can add fields in the __init__ of model form, to perfom some logic
            # No need to del this field manually, django will neglect this field
            # because it is not in the fields list of model form
            # del PersonalInfo["condition"]

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
            return HttpResponseRedirect("http://127.0.0.1:9000")

        else:
            PersonalInfo = form_list[0].cleaned_data
            PersonalInfo.save(commit=False)
            del PersonalInfo["condition"]

            publication_data = form_list[2].cleaned_data
            over_view = form_list[3].cleaned_data
            education_data = form_list[4].cleaned_data
            job_data = form_list[5].cleaned_data
            job_accomplishment_data = form_list[6].cleaned_data
            skill_and_skill_level_data = form_list[7].cleaned_data
            programming_area_data = form_list[8].cleaned_data
            projects_data = form_list[9].cleaned_data

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

            return HttpResponseRedirect("http://127.0.0.1:9000")






class PersonalInfo_List_CreateView(viewsets.ModelViewSet):
    queryset = PersonalInfo.objects.order_by("-id")
    lookup_field = "id"
    serializer_class = PersonalInfo_Serializer
    pagination_class = LargeResultsSetPagination
    authentication_classes = [JWTStatelessUserAuthentication]
    permission_classes = [IsAuthenticated]


     

    def perform_update(self, serializer):
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

        print(f"user_id : {user_id} and id : {id}")

        try:
            with transaction.atomic():
                # raise Exception("Simulated server crash")
                super().perform_update(serializer)
                if user_id:
                    transaction.on_commit(lambda:(self.send_notification(event="cv_updated", 
                                                    status_ = "UPDATED",
                                                    exception = None, user_id = user_id,
                                                    id = id))) 
                else:
                    transaction.on_commit(lambda:(self.send_notification(event="cv_updated", 
                                                                         status_ = "UPDATED",
                                                                        id = id,
                                                                        exception=None, user_id=None))) 
        except Exception as e:
            return self.send_notification(event="cv_update_fail", exception = str(e), status_="FAILED",
                                            user_id = user_id if user_id else None, id = id)

    def destroy(self, request, *args, **kwargs): 
        personal_info_id = kwargs['id']
        print(f"personal_info_id__________delete___{personal_info_id}")
        personal_info = PersonalInfo.objects.filter(id = personal_info_id)
        id_user = None
        id = None

        if personal_info:
            id_user = personal_info[0].user_id.id
            try:
                with transaction.atomic():
                    super().destroy(request, *args, **kwargs)
                transaction.on_commit(lambda:(self.send_notification(event="cv_deleted", 
                                                        status_ = "DELETED",
                                                        exception = None, 
                                                        user_id = id_user, id = personal_info_id))) 
            except Exception as e:
                return self.send_notification(event="cv_deletion_failed", exception = str(e), 
                                                        status_="FAILED",
                                                        user_id = id_user, id = personal_info_id)
        else:
            # return self.send_notification(event="cv_deletion_failed", exception = "Personal Info does not exist", 
            #                                             status_="FAILED",
            #                                             user_id = id_user, id = personal_info_id)
            return Response({"error": "Personal Info does not exist"}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=False, methods=['GET'])
    def get_personal_info_for_user(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        personal_info_id = request.query_params.get('personal_info_id')
        
        filter_kwargs = {}
        try:
            if personal_info_id:
                queryset = self.get_queryset().filter(id=personal_info_id, user_id=user_id)
                filter_kwargs = {"user_id": user_id,
                             "id": personal_info_id}
            else:
                queryset = self.get_queryset().filter( user_id=user_id)
                filter_kwargs = {"user_id": user_id,
                            }

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return JsonResponse({"error":str(e)})


    @action(detail=False, methods=['PATCH', 'PUT'])
    def patch_personal_info_for_user(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        id = request.query_params.get('id')
        print(f"user_id : {user_id} and id : {id}")

        try:
            if user_id:
                partial = kwargs.pop('partial', False)
                instance = PersonalInfo.objects.filter(user_id__id=user_id, id =id)
                
                if instance:
                    data = request.data
                    if user_id not in data:
                        data["user_id"] = user_id
                    # want to pass/access variables / keys / query parameters from ModelSets method to/within
                    # crete(), ppdate() method of Serializer class, then pass these in context dictionary
                    
                    serializer = self.get_serializer(instance[0], data=data, partial=partial,
                                                    context = {"user_id" : user_id, "id" : id})

                    serializer.is_valid(raise_exception=True)
                    self.perform_update(serializer)
                    return Response(serializer.data)
                else:
                    return Response({"error" : "Personal Info does not exist"})
            else:
                return Response({"error" : "user_id not provided"})
        except Exception as e:
            return Response (str(e))


    def send_notification(self, event, **kwargs):
        webhook_url = "http://127.0.0.1:9000/cv-webhook/"  
        headers = {"Content-Type": "application/json"}

        if event == "cv_deleted" or event == "cv_deletion_failed": 

            user_id = kwargs["user_id"]
            id = kwargs["id"]
            print(f"user_id = {user_id} and id = {id}")
        

        elif event == "cv_updated" or event == "cv_update_fail":

            if kwargs["user_id"] and kwargs["user_id"] is not None:
                id = kwargs["id"]
                user_id = kwargs["user_id"]
            else:
                user_id = None

        else: pass


        data = {'id': id,
                'user_id': user_id,
                "event":  event,
                "status" : kwargs["status_"],
                "exception" : kwargs["exception"] or str("None")} 


        data = json.dumps(data)        

        response = requests.post(webhook_url, headers=headers ,data=data)
        if response.status_code == 200:
            return JsonResponse({"message": "Webhook sent successfully"})
        else:
            return JsonResponse({"error": "Failed to send webhook"}, status=500)







from django.core.files.storage import FileSystemStorage
from formtools.preview import FormPreview
from resume.forms import PersonalInfoForm, PublicationForm, OverviewForm


class PersonalInfoPreviewWizard(FormPreview):
    form_template = "wizard_view_form.html"
    preview_template = "preview_wizard.html"

    def done(self, request, cleaned_data):
        print(cleaned_data)
        del cleaned_data["condition"]
        print(cleaned_data)
        info_instance = PersonalInfo.objects.create(**cleaned_data)
        return HttpResponseRedirect("/page-to-redirect-to-when-done/")


from django.views import View


class PersonalInfoView(View):

    def get(self, request, **kwargs):
        form = PersonalInfoForm()
        return render(self.request, "form_form.html", {"form": form})

    def post(self, request, **kwargs):
        if request.method == "POST":
            print(request.POST.dict())
            form = PersonalInfoForm(request.POST)
            if form.is_valid():
                print(f"************{form.cleaned_data}")
                del form.cleaned_data["condition"]
                print(form.cleaned_data)
                commit_form = form.save(commit=False)
                print(f"___________{commit_form}")
                commit_form.save()
        return HttpResponseRedirect("/page-to-redirect-to-when-done/")


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Projects
from .serializers import ProjectsSerializer


@csrf_exempt
def project_create(request):
    if request.method == "POST":
        # Deserialize the JSON data sent in the request
        data = request.POST.dict()
        serializer = ProjectsSerializer(data=data)

        # Check if the data is valid
        if serializer.is_valid():
            # Save the validated data
            serializer.save()
            # Return a success response with the saved data
            return JsonResponse(serializer.data, status=201)
        else:
            # Return an error response with the validation errors
            return JsonResponse(serializer.errors, status=400)
    else:
        # Return a method not allowed response for requests other than POST
        return JsonResponse({"error": "Method not allowed"}, status=405)



