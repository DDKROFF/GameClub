from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('news/', include('news.urls')),
    path('devices/', include('devices.urls')),
    path('', include('main.urls'), name='home'),
    path('users/', include('users.urls', namespace='users')),
]