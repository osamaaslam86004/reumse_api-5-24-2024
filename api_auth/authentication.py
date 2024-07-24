from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class CSRFTrustedOriginAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        Authenticate the request based on CSRF_TRUSTED_ORIGINS.
        """
        # Check if the request's origin is allowed in CSRF_TRUSTED_ORIGINS
        origin = request.headers.get("Origin")
        if origin not in getattr(settings, "CSRF_TRUSTED_ORIGINS", []):
            raise AuthenticationFailed("Origin not trusted")

        # Return None, since no user is authenticated with CSRF token
        return None
