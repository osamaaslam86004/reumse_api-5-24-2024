from django.urls import path, include
from resume import views
from resume.views import (
    PersonalInfo_List_CreateView,
    PersonalInfoViewSet,
    OverviewViewSet,
    EducationViewSet,
    SkillViewSet,
    ProgrammingAreaViewSet,
    ProjectsViewSet,
    PersonalInfoWizard,
    PersonalInfoView,
    PersonalInfo_List_CreateView,
    PersonalInfoPreviewWizard
)
from resume.forms import PersonalInfoForm
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register(r"personal-info-data", PersonalInfoViewSet)
router.register(r"get-personal-info-data", PersonalInfo_List_CreateView, basename='get-personal-info-data')
router.register(r"overview", OverviewViewSet)
router.register(r"education", EducationViewSet)
router.register(r"skill", SkillViewSet)
router.register(r"programming_area", ProgrammingAreaViewSet)
router.register(r"projects", ProjectsViewSet)


urlpatterns = [


    path("get-personal-info-data-for-user/", PersonalInfo_List_CreateView.as_view({
                                                                       'get': 'list',
                                                                       'get' : 'get_personal_info_for_user'}),
                                                                        name ="get_personal_info_for_user"),
                                                                        
    path("patch-put-personal-info-data-for-user/", PersonalInfo_List_CreateView.as_view({
                                                                       'put': 'patch_personal_info_for_user',
                                                                       'patch' : 'patch_personal_info_for_user'}),
                                                                        name ="patch_put_personal_info_for_user"),

                                                                        
    path(
        "",
        PersonalInfoWizard.as_view(),
        name="personal-info-wizard",
    ),

    path(
        "preview/",
        views.PersonalInfoPreviewWizard(PersonalInfoForm),
        name="personal-info-preview_wizard",
    ),
    path(
        "form/",
        PersonalInfoView.as_view(),
        name="personal-info-view",
    ),

] + [path("api/", include(router.urls))]

