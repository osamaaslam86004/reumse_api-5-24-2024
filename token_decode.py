import os
from django.conf import settings

# Manually configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_api.settings')  # Replace 'your_project_name' with your actual Django project name

# Initialize Django settings
import django
django.setup()


from rest_framework_simplejwt.tokens import AccessToken

# Problem: token claim not in token
# advice: after making changes to token / token tables, apply the migrations again!
# re-applying migrations after deleting cache file, solved the problem 
token_string = {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwODUyODU5NSwiaWF0IjoxNzA4NDQyMTk1LCJqdGkiOiJlOTM0YmY3MWI1YjE0OTYyOGU0ZDJjMjJmMzViOTBlZCIsInVzZXJfaWQiOjMsInVzZXIiOiJzZWxsZV9fNSJ9.WkN4x0-rc41u8A8KlsIcfb_kv9WGtJQLyEfD1kwb2sg",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA4NDQyNDk1LCJpYXQiOjE3MDg0NDIxOTUsImp0aSI6IjcxNDBhZDJlNDBlZDQ0MjI5Mjc0NTc3MzY4MjlhYmJkIiwidXNlcl9pZCI6MywidXNlciI6InNlbGxlX181In0.VejZLIR5f6oC34rVFgDb_hdaPPzGMqTMGdjbQyXxH4A"
}




SIGNING_KEY =  "django-insecure-o_j80u+4owpa-&!$%&j&n@r0d6&)9kbutwi!m&j-v*b(ems*=d"
import jwt
decoded_access_token = jwt.decode(token_string["access"],  SIGNING_KEY ,algorithms =  "HS256")
                                    # options={"verify_signature": False}) 

# Print the decoded token
print(decoded_access_token)

# {'token_type': 'access', 'exp': 1708442495, 'iat': 1708442195, 'jti': '7140ad2e40ed4422927457736829abbd', 'user_id': 3, 'user': 'selle__5'}


