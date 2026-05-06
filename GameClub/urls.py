from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('js/', admin.site.urls),
    path('', include('main.urls')),
]