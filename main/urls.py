from django.urls import path

from devices import views as devices
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('halls/map/', devices.halls_map, name='hallMap'),
    path('api/statuses/all/', devices.api_status_all, name='api_status_all'),
]
