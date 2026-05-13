from django.urls import path, include
import users.views

urlpatterns = [
    path('signin/', users.views.login_view, name='signin'),
    path('signup/', users.views.register_view, name='signup'),
]