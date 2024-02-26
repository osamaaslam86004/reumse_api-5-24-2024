

from django.db.models.signals import post_save
from django.dispatch import receiver
from resume.models import PersonalInfo
import json, requests



 
@receiver(post_save, sender=PersonalInfo) 
def create_profile(sender, instance,  **kwargs):
    if instance:
        data = {'id': instance.id,
            'user_id': instance.user_id.id,
            "event":  "cv_created",
            "status" : "CREATED",
            "exception" : str("None")} 


        data = json.dumps(data)        

        webhook_url = "http://127.0.0.1:9000/cv-webhook/"  
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(webhook_url, headers=headers, data=data)
            response.raise_for_status()  # Raise an exception for any HTTP error status
            print("Webhook sent successfully")
        except requests.exceptions.RequestException as e:
            print("Failed to send webhook:", e)

