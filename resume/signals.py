

from django.db.models.signals import post_save
from django.dispatch import receiver
from resume.models import PersonalInfo
import json
import requests
from django.db.models.signals import pre_delete, post_delete




class TemporaryStorage:
    storage = {}



@receiver(post_save, sender=PersonalInfo)
def create_profile(sender, instance,  **kwargs):
    if instance:
        data = {'id': instance.id,
            'user_id': instance.user_id.id,
            "event":  "cv_created",
            "status" : "CREATED",
            "exception" : str("None")}


        data = json.dumps(data)

        # webhook_url = "https://osama11111.pythonanywhere.com/cv-webhook/"
        webhook_url = "https://diverse-intense-whippet.ngrok-free.app/cv-webhook/"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(webhook_url, headers=headers, data=data)
            response.raise_for_status()  # Raise an exception for any HTTP error status
            print("Webhook sent successfully")
            print(f"response status-----: {response.json()} and status code---- : {response.status_code}")
        except requests.exceptions.RequestException as e:
            print("Failed to send webhook:", e)




# Question:
        # How to create a pre_delete signal that collect these attributes 'cv_id': instance.id,  'user_id': instance.user_id.id,]
        # # and pass on these attibutes values to post_delete signal mentioned in the previous prompt

# Answar:
        # To achieve this, you can store the necessary attributes in a temporary location (e.g., a cache or a class-level variable) in the pre_delete signal and then access these stored attributes in the post_delete signal.

        # Here’s how you can implement this:

        # Define a class-level dictionary to store the attributes.
        # Use pre_delete to capture and store the attributes.
        # Use post_delete to send the webhook using the stored attributes.





@receiver(pre_delete, sender=PersonalInfo)
def store_cv_attributes(sender, instance, **kwargs):
    TemporaryStorage.storage[instance.id] = {
        'cv_id': instance.id,
        'user_id': instance.user_id.id,
    }



@receiver(post_delete, sender=PersonalInfo)
def send_webhook_on_cv_delete(sender, instance, **kwargs):
    attributes = TemporaryStorage.storage.pop(instance.id, None)

    webhook_url = "https://diverse-intense-whippet.ngrok-free.app/cv-webhook/"
    data = {
        'event': 'cv_deleted',
        'id': attributes['cv_id'],
        'user_id': attributes['user_id'],
        # 'deleted_at': instance.deleted_at.isoformat()
    }

    data = json.dumps(data)
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(webhook_url, headers=headers, data=data)
        response.raise_for_status()
        print(f"client response status for handling webhook: {response.raise_for_status()}")
    except requests.RequestException as e:
        # Handle the exception (log it, notify someone, etc.)
        print(f"Failed to send webhook: {e}")

























