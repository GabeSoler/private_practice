from django.urls import path,include
from . import views

app_name = "ai_chat"
urlpatterns = [
    path("",views.index,name="index")
]
