from django.urls import path, include
from resume import views
from resume.views import (
    PersonalInfo_List_CreateView,
    PersonalInfoWizard,
    # PersonalInfoView,
    # PersonalInfoPreviewWizard
)

# from resume.forms import PersonalInfoForm
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(
    r"get-personal-info-data",
    PersonalInfo_List_CreateView,
    basename="get-personal-info-data",
)
urlpatterns = [
    path(
        "get-personal-info-data-for-user/",
        PersonalInfo_List_CreateView.as_view({'get' : 'get-personal-info-data-for-user'}),
        name="get_personal_info_for_user",
    ),
    path(
        "patch-put-personal-info-data-for-user/",
        PersonalInfo_List_CreateView.as_view(
            {
                "put": "patch_personal_info_for_user",
                "patch": "patch_personal_info_for_user",
            }
        ),
        name="patch_put_personal_info_for_user",
    ),
    path(
        "",
        PersonalInfoWizard.as_view(),
        name="personal-info-wizard",
    ),
] + [path("api/", include(router.urls))]


# path(
#     "preview/",
#     views.PersonalInfoPreviewWizard(PersonalInfoForm),
#     name="personal-info-preview_wizard",
# ),
# path(
#     "form/",
#     PersonalInfoView.as_view(),
#     name="personal-info-view",
# ),
