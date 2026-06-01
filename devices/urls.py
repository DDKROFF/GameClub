from django.urls import path
from . import views
from devices import views as devices

urlpatterns = [
    path('halls/map/', views.halls_map, name='halls_map'),
]