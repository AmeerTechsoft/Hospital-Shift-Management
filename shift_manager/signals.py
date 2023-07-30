from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.sites.models import Site
from notify.signals import notify

from .models import Shift

@receiver(post_save, sender=Shift)
def send_complaint_notification(sender, instance, **kwargs):
    if instance.complaint:
        current_site = Site.objects.get_current()
        notify.send(instance, recipient=None, verb=f"New complaint received: {instance.complaint}", target=current_site)
