
# signals.py

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import BlogUser


# for createing bloguser object when user object is created
@receiver(post_save, sender=User)
def create_bloguser_for_superuser(sender, instance, created, **kwargs):
    if created:
        BlogUser.objects.create(user=instance)