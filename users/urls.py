from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signin/', views.login_view, name='signin'),
    path('signup/', views.register_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]