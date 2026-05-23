from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import RoomCalendarModel, TenantModel
from django.db.models.signals import post_save
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=get_user_model())
def signal_setup_room_calendar(sender, **kwargs):
    created = True  # if created is false in one of the bellows stops the process as it already happened
    while created:
        user = kwargs['instance']
        base_room, created = RoomCalendarModel.objects.get_or_create(user=user,
                                                                     name="Base Room",
                                                                     description="Default room calendar"
                                                                     )
        base_tenant, created = TenantModel.objects.get_or_create(user=user,
                                                                 name=user.username,
                                                                 display_name=user.username,
                                                                 calendar=base_room)
        logger.info("Created base room calendar and base tenant")
