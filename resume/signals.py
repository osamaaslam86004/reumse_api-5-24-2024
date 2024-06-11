from django.db.models.signals import post_save
from django.dispatch import receiver
from resume.models import PersonalInfo
import json
import requests
from django.db.models.signals import pre_delete, post_delete
from django.conf import settings


class TemporaryStorage:
    storage = {}


@receiver(post_save, sender=PersonalInfo)
def create_profile(sender, instance, **kwargs):
    # Assuming the instance has a serializer set with the is_create attribute
    serializer = kwargs.get("serializer", None)
    if not serializer or not getattr(serializer, "is_create", False):
        return  # Exit the signal if not a create operation

    if instance:
        data = {
            "id": instance.id,
            "user_id": instance.user_id.id,
            "event": "cv_created",
            "status": "CREATED",
            "exception": str("None"),
        }

        data = json.dumps(data)

        if not settings.DEBUG:
            webhook_url = "https://osama11111.pythonanywhere.com/cv-webhook/"
        else:
            webhook_url = "https://diverse-intense-whippet.ngrok-free.app/cv-webhook/"

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(webhook_url, headers=headers, data=data)
            response.raise_for_status()  # Raise an exception for any HTTP error status
            print("Webhook sent successfully")
            print(
                f"response status-----: {response.json()} and status code---- : {response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            print("Failed to send webhook:", e)


@receiver(pre_delete, sender=PersonalInfo)
def store_cv_attributes(sender, instance, **kwargs):
    TemporaryStorage.storage[instance.id] = {
        "cv_id": instance.id,
        "user_id": instance.user_id.id,
    }


@receiver(post_delete, sender=PersonalInfo)
def send_webhook_on_cv_delete(sender, instance, **kwargs):
    attributes = TemporaryStorage.storage.pop(instance.id, None)

    if not settings.DEBUG:
        webhook_url = "https://osama11111.pythonanywhere.com/cv-webhook/"
    else:
        webhook_url = "https://diverse-intense-whippet.ngrok-free.app/cv-webhook/"

    data = {
        "event": "cv_deleted",
        "id": attributes["cv_id"],
        "user_id": attributes["user_id"],
        # 'deleted_at': instance.deleted_at.isoformat()
    }

    data = json.dumps(data)
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(webhook_url, headers=headers, data=data)
        response.raise_for_status()
        print(
            f"client response status for handling webhook: {response.raise_for_status()}"
        )
    except requests.RequestException as e:
        # Handle the exception (log it, notify someone, etc.)
        print(f"Failed to send webhook: {e}")
