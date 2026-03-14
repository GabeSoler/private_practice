from django.urls import path, include
from .views import index_view, set_language_wrapper_view

app_name = 'base'

urlpatterns = [
    # Home page
    path('', index_view, name='index'),
    path('set_language', set_language_wrapper_view, name='set_language'),
]
