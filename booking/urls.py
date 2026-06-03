from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('deposit/', views.deposit_view, name='deposit'),
    path('transactions/', views.transaction_history, name='transactions'),
    path('bookings/', views.active_bookings, name='bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]