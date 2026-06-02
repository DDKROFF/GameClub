from django.urls import path
from . import views

urlpatterns = [
    path('signin/', views.login_view, name='signin'),
    path('signup/', views.register_view, name='signup'),
]