from django.urls import path
from . import views
from devices import views as devices


app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('halls/map/', devices.halls_map, name='hallMap'),
]