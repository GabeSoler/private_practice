from django.contrib.auth import get_user_model

from session_client import models
import pendulum as p


def create_sessions(day=0):
    """ creates a full day of sessions """
    today = p.now().add(days=day)
    sessions = []
    user,_ = get_user_model().objects.get_or_create(username="Gabe")
    room = models.RoomCalendarModel.objects.get(name="Base Room",user=user)
    client,_ = models.ClientModel.objects.get_or_create(user=user,code="Test123",
                                                      time=today.at(8,0).time(),
                                                      duration=p.duration(hours=1))
    for i in range(9,21):
        session = models.SessionModel(
            client=client,
            date=today.date(),
            start_time=today.at(i).time(),
            end_time=today.at(i+1).time(),
            keywords=f"Test Session {i}",
            calendar=room
        )
        sessions.append(session)
    models.SessionModel.objects.bulk_create(sessions)