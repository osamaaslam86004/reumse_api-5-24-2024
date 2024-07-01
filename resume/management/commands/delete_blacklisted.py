from django.core.management.base import BaseCommand
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)


class Command(BaseCommand):
    help = "Delete all tokens in the OutstandingToken table that have been blacklisted"

    def handle(self, *args, **kwargs):

        blacklisted_tokens = BlacklistedToken.objects.values_list("token_id", flat=True)
        deleted, _ = OutstandingToken.objects.filter(
            token_id__in=blacklisted_tokens
        ).delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {deleted} blacklisted outstanding tokens"
            )
        )

        count, _ = BlacklistedToken.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted {count} blacklisted tokens")
        )
