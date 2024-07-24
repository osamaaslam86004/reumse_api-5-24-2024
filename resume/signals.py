from django.db.models.signals import post_save
from django.dispatch import receiver
from resume.models import PersonalInfo
import json
import requests
from django.db.models.signals import pre_delete, post_delete
from django.conf import settings
import logging
from requests.adapters import HTTPAdapter, Retry

logger = logging.getLogger(__name__)


class TemporaryStorage:
    storage = {}


@receiver(post_save, sender=PersonalInfo)
def create_profile(sender, instance, **kwargs):

    _serializer = kwargs.get("serializer", None)

    # Check if the serializer exists and if it's a create operation
    if _serializer and not getattr(_serializer, "is_create", False):
        return

    logger.error(f"serializer: {_serializer}---- : is_create : {getattr(_serializer, 'is_create', False)}")
    print(f"serializer: {_serializer}---- : is_create : {getattr(_serializer, 'is_create', False)}")

    if instance:
        data = {
            "id": instance.id,
            "user_id": instance.user_id.id,
            "event": "cv_created",
            "status": "CREATED",
            "exception": str("None"),
        }

        data = json.dumps(data)
        logger.error(f"data in signal: {data}")

        if settings.DEBUG:
            webhook_url = "https://osama11111.pythonanywhere.com/cv-webhook/"
        else:
            webhook_url = "https://diverse-intense-whippet.ngrok-free.app/cv-webhook/"

        headers = {"Content-Type": "application/json"}

        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=0.1, status_forcelist=[504, 500, 502, 503]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))

        try:
            response = requests.post(
                webhook_url, headers=headers, data=data, verify=False
            )
            response.raise_for_status()  # Raise an exception for any HTTP error status
            logger.info(
                f"Webhook sent successfully: {response.json()} and status code: {response.status_code}"
            )

        except requests.exceptions.RequestException as e:
            print("Failed to send webhook:", e)
            logger.error(f"Failed to send webhook: {e}")


@receiver(pre_delete, sender=PersonalInfo)
def store_cv_attributes(sender, instance, **kwargs):
    TemporaryStorage.storage[instance.id] = {
        "cv_id": instance.id,
        "user_id": instance.user_id.id,
    }


@receiver(post_delete, sender=PersonalInfo)
def send_webhook_on_cv_delete(sender, instance, **kwargs):
    attributes = TemporaryStorage.storage.pop(instance.id, None)

    if settings.DEBUG:
        webhook_url = "https://osama11111.pythonanywhere.com/cv-webhook/"
    else:
        webhook_url = "https://diverse-intense-whippet.ngrok-free.app/cv-webhook/"

    data = {
        "event": "cv_deleted",
        "id": attributes["cv_id"],
        "user_id": attributes["user_id"],
    }
    logger.error(f"Data to send webhook: {data}")

    data = json.dumps(data)
    headers = {"Content-Type": "application/json"}

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[504, 500, 502, 503])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = requests.post(webhook_url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        logger.info(
            f"Webhook sent successfully: {response.json()} and status code: {response.status_code}"
        )
    except requests.RequestException as e:
        print(f"Failed to send webhook: {e}")
        logger.error(f"Failed to send webhook: {e}")
