from django.urls import path
from . import views
from devices.views import (
    ClubMapView,
    HallListView, HallDetailView, HallCreateView, HallUpdateView, HallDeleteView,
    DeviceListView, DeviceDetailView,
    ComputerListView, ComputerDetailView,
    ConsoleListView, ConsoleDetailView,
)

app_name = 'main'

urlpatterns = [
    # главная
    path('', views.IndexView.as_view(), name='home'),

    # карта клуба (новая)
    path('halls/map/', ClubMapView.as_view(), name='hallMap'),

    # залы
    path('halls/', HallListView.as_view(), name='hall_list'),
    path('halls/<int:pk>/', HallDetailView.as_view(), name='hall_detail'),
    path('halls/create/', HallCreateView.as_view(), name='hall_create'),
    path('halls/<int:pk>/update/', HallUpdateView.as_view(), name='hall_update'),
    path('halls/<int:pk>/delete/', HallDeleteView.as_view(), name='hall_delete'),
    path('devices/', DeviceListView.as_view(), name='device_list'),
    path('devices/<int:pk>/', DeviceDetailView.as_view(), name='device_detail'),
    path('computers/', ComputerListView.as_view(), name='computer_list'),
    path('computers/<int:pk>/', ComputerDetailView.as_view(), name='computer_detail'),
    path('consoles/', ConsoleListView.as_view(), name='console_list'),
    path('consoles/<int:pk>/', ConsoleDetailView.as_view(), name='console_detail'),
]