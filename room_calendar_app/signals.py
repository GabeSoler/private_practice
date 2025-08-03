from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import RoomCalendarModel,TenantModel
from django.db.models.signals import post_save

@receiver(post_save, sender=get_user_model())
def signal_setup_room_calendar(sender, **kwargs):
    created = True
    while created is True:
        base_tenant,created = TenantModel.objects.get_or_create(user=kwargs['instance'],name="Default")
        base_room,created = RoomCalendarModel.objects.get_or_create(user=kwargs['instance'],
                                                name="Base Room",
                                                description="Default room calendar"
                                                )
        base_room.tenants.add(base_tenant)




