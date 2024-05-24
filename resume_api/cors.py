
from django.conf import settings
from django.http import HttpResponse
import logging
logger = logging.getLogger(__name__)



class CustomCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        self.allowed_headers = getattr(settings, 'CORS_ALLOW_HEADERS', [])
        self.trusted_csrf_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
        self.allowed_methods = getattr(settings, 'CORS_ALLOW_METHODS', [])
        self.host_url = "osamaaslam.pythonanywhere.com"

    def __call__(self, request):
        origin = request.headers.get('Origin')
        logger.info(f"Request Origin: {origin}")
        host = request.headers.get('Host')
        logger.info(f"Request Host: {host}")


        # A preflight request is made when the actual request falls into one of the following categories:

        #     1.     When your application uses methods other than GET, HEAD, or POST, the browser will initiate a preflight
        #     request to ask the server for permission before sending the actual request.
        #     2.     Custom headers: If your request includes headers that are not included in the simple headers defined in
        #     the CORS specification, a preflight request will be sent.

        #     An HTTP OPTIONS request that includes additional information about the intended request,
        #     such as HTTP method, headers, and content type, is referred to as a preflight request.
        #     The server receiving the preflight request must respond with CORS headers indicating whether
        #     the actual request should be permitted. In these headers, "Access-Control-Allow-Origin" specifies
        #     the allowed origins, "Access-Control-Allow-Methods" specifies the allowed HTTP methods, and "Access-Control-Allow-Headers"
        #     specifies the allowed headers.

        # Combine both allowed origins and CSRF trusted origins
        combined_origins = self.allowed_origins + self.trusted_csrf_origins     # this will allow CORS to submit forms using CSRF token validation
        logger.info(f"Combined Origins: {combined_origins}")

        # Check if the origin is allowed
        if origin in combined_origins:
            if request.method == 'OPTIONS':
                response = HttpResponse()
                response["Access-Control-Allow-Origin"] = origin
                response["Access-Control-Allow-Methods"] = ', '.join(self.allowed_methods)
                response["Access-Control-Allow-Headers"] = ', '.join(self.allowed_headers)
                response["Access-Control-Allow-Credentials"] = 'true'
                response["Access-Control-Max-Age"] = 86400
                response["Access-Control-Expose-Headers"] = "*"

            else:
                response = self.get_response(request)
                response["Access-Control-Allow-Origin"] = origin
                response["Access-Control-Allow-Methods"] = ', '.join(self.allowed_methods)
                response["Access-Control-Allow-Headers"] = ', '.join(self.allowed_headers)
                response["Access-Control-Allow-Credentials"] = 'true'

        elif host == self.host_url:
             response = self.get_response(request)
        else:
            response = HttpResponse("Origin not allowed", status=403)

        return response

