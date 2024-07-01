from django.core.management.base import BaseCommand
import logging
from django.db.models import Count
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Delete all tokens in the OutstandingToken table that have been blacklisted"

    def handle(self, *args, **kwargs):
        token_id = OutstandingToken.objects.values("user_id")

        print(f"Returns Queryset-- : {token_id}")

        # return a Queryset list of dictionary with key, values
        token_data = OutstandingToken.objects.values("jti", "user_id", "id")
        print(f"token_data----- : {token_data}")

        for token in token_data:
            jti = token["jti"]
            user_id = token["user_id"]
            id = token["id"]
            print(f"jti : {jti}---- user_id : {user_id}---- id: {id}")

        # Returns <QuerySet [{'jti': '23c3ca86705844a0bacc1424d4550b32', 'user_id': 3, 'id': 1, 'users': 1},
        annotate_data = token_data.annotate(users=Count("user_id"))
        print(f"annotated_data----- : {annotate_data}")

        ############################################################################################
        #   ----- Values_list()-------
        ###########################################################################################

        # return a list of tuples
        # <QuerySet [(3,), (3,), (3,), (3,), (4,), (4,), (4,), (4,), (4,)]>
        token_id = OutstandingToken.objects.values_list("user_id")

        print(f"token ids without flat=False-- : {token_id}")

        # returns a list
        # <QuerySet [3, 3, 3, 3, 4, 4, 4, 4, 4]>
        token_id = OutstandingToken.objects.values_list("user_id", flat=True)

        print(f"token ids without flat=true-- : {token_id}")

        try:
            #  'flat' is not valid when values_list is called with more than one field.
            token_id = OutstandingToken.objects.values_list(
                "jti", "user_id", "id", flat=True
            )
        except:
            # Always Returns a tuple
            outstanding_token_data = OutstandingToken.objects.values_list(
                "jti", "user_id", "id"
            )

            for jti, user_id, id in outstanding_token_data:
                print(f"jit : {jti}-----user_id : {user_id}----id: {id}")
