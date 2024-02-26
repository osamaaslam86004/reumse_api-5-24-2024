
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from api_auth.views import UserCreateView, MyTokenObtainPairView
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register(r"crud-user", UserCreateView,  basename='crud-user' )


urlpatterns = [
    # get the access token
    path('token/',  MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # provide user details with refresh token to get new access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


] + [path("", include(router.urls))]