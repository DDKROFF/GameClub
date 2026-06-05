from django.urls import path
from . import views

app_name = 'news'
urlpatterns = [
    path('', views.news_list, name='list'),
    path('<int:news_id>/like/', views.news_like, name='like'),
    path('<int:news_id>/dislike/', views.news_dislike, name='dislike'),
    path('<int:news_id>/view/', views.news_view, name='view'),
    path('calendar', views.CalendarView.as_view(), name='calendar'),
]