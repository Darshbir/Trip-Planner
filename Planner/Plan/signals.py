import re
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import BITSUser
from .views import parse_email

@receiver(post_save, sender=User)
def create_bits_user(sender, instance, created, **kwargs):
    if created:
        email = instance.email
        parsed_data = parse_email(email)
        if parsed_data:
            BITSUser.objects.create(
                user=instance,
                bits_id=parsed_data['id'],
                campus=parsed_data['campus'],
                batch=parsed_data['batch']
            )
