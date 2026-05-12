from django.contrib import admin
from django.urls import path, include
import users.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('login/', users.views.login_view, name='login')
]