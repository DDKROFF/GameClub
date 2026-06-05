from django.urls import path
from . import views

app_name = 'booking' # Убедись, что это имя совпадает с тем, что в шаблоне {% url 'booking:device_action' %}

urlpatterns = [
    path('session-form/', views.session_form_page, name='session_form'),
    path('device-action/', views.device_action, name='device_action'),
]