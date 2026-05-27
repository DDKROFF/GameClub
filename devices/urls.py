from django.urls import path
from . import views

urlpatterns = [
    path('halls/map/', views.halls_map, name='halls_map'),
    path('api/statuses/all/', views.api_get_all_statuses, name='api_all_statuses'),
]