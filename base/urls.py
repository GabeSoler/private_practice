from django.urls import path, include
from .views import index_view, set_language_wrapper_view, about_view, data_policy_view

app_name = 'base'

urlpatterns = [
    # Home page
    path('', index_view, name='index'),
    path('about', about_view, name='about'),
    path('data-policy', data_policy_view, name='data_policy'),
    path('set_language', set_language_wrapper_view, name='set_language'),
]
