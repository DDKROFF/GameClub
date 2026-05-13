from django.contrib import admin
from django.urls import path, include
import users.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls'), name='home'),
    path('auth/', include('users.urls')),
]