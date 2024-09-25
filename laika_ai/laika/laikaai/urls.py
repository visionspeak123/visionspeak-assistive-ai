# urls.py (App Level)

from django.urls import path
from . import views
from .views import email_view

urlpatterns = [
    path('', views.index, name='index'),
    path('explore/', views.explore, name='explore'),
    
    path('object/', views.object_detection_view, name='object_detection'),
    path('weather/', views.weather_view, name='weather'),
    path('navigation/', views.navigation_view, name='navigation'),
    path('chat/', views.chat_view, name='chat'),
     path('email/', views.email_view, name='email'),
     path('compose-email', views.compose_email, name='compose_email'),
    path('read-email', views.read_email, name='read_email'),
    path('delete-email', views.delete_email, name='delete_email'),
     path('current_time/', views.get_current_time_view, name='current_time'),
     path('process_command/', views.process_command, name='process_command'),
      path('get_joke/', views.get_joke, name='get_joke'),
     path('get_person_info/', views.get_person_info, name='get_person_info'),
    path('place_info/', views.place_info, name='place_info'),
    
     
]
        


