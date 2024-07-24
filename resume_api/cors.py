from django.conf import settings
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class CustomCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])
        self.trusted_csrf_origins = getattr(settings, "CSRF_TRUSTED_ORIGINS", [])
        self.host_url = [
            "osamaaslam.pythonanywhere.com",
            "diverse-intense-whippet.ngrok-free.app",
            "e.com",
        ]
        logger.info(f"Host URL: {self.host_url}")

    def __call__(self, request):
        origin = request.headers.get("Origin")
        logger.info(f"Request Origin: {origin}")

        host = request.headers.get("Host")
        logger.info(f"Request Host: {host}")

        # Combine both allowed origins and CSRF trusted origins
        combined_origins = self.allowed_origins + self.trusted_csrf_origins
        logger.info(f"Combined Origins: {combined_origins}")

        response = self.process_request_before_process_view(
            request, combined_origins, host, origin
        )
        if response:
            return response
        else:
            response = self.get_response(request)
            response = self.process_response(request, response)
            return response

    def process_request_before_process_view(
        self, request, combined_origins, host, origin
    ):
        """
        process the request before self.process_view() is called
        """

        if origin is None and host in self.host_url:
            logger.info(
                f"Server--------------{request.headers.get('Server', '').lower() }"
            )
            if (
                request.headers.get("Server")
                and request.headers.get("Server") != "PythonAnywhere"
            ):
                return JsonResponse({"detail": "Origin not allowed"}, status=403)
            return None

        if origin in combined_origins and host in self.host_url:
            return None

        if origin in combined_origins or host in self.host_url:
            if (
                request.headers.get("Referer")
                == "https://osamaaslam.pythonanywhere.com/api/schema/swagger-ui/"
            ):
                return None

        if origin is None:
            if request.headers.get("Referer") == "http://127.0.0.1:5500":
                return None

        return JsonResponse({"detail": "Origin not allowed"}, status=403)

    def process_response(self, request, response):

        # Do not enforce Origin if it's already set correctly
        origin = request.headers.get("Origin")
        if origin:
            response["Access-Control-Allow-Origin"] = origin

        # Do not enforce Content-Type if it's already set correctly
        if response.get("Content-Type", "").startswith("application/json"):
            response["Content-Type"] = "application/json"

        if "Allow" in response.headers:
            response["Access-Control-Allow-Methods"] = response.headers["Allow"]

        # Remove "Cookie" from SessionMiddleWare
        # vary_headers = response.headers.get("Vary", "").split(", ")
        # if "Cookie" in vary_headers:
        #     vary_headers.remove("Cookie")
        # response.headers["Vary"] = ", ".join(vary_headers)

        response["Access-Control-Allow-Credentials"] = "true"

        # Extract all headers and format them as a comma-separated string
        allow_headers = ", ".join(response.headers.keys())
        response["Access-Control-Allow-Headers"] = allow_headers

        for header in response.headers:
            logger.info(
                f"header coming out of API: {header}--------- : {response.headers[header]}"
            )

        return response


# Notes

# Access-Control-Allowed-Headers in response:
# it is a dictionay of all allowed headers alongwith the header values

# {
# 'Content-Type': 'application/json',
# 'X-RateLimit-Limit': '2/hour',
# 'X-RateLimit-Remaining': '1',
#  'Allow': 'POST, OPTIONS',
#  'Vary': 'User-Agent, Cookie',
# 'Cache-Control': 'private',
#  'X-Frame-Options': 'DENY',
# 'Content-Length': '104',
# 'X-Content-Type-Options': 'nosniff',
#  'Referrer-Policy': 'same-origin', 'Cross-Origin-Opener-Policy': 'same-origin',
#  'Access-Control-Allow-Origin': 'https://web.postman.co'

# }
