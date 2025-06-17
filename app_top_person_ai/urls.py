from django.urls import path
from . import views

app_name="app_top_person_ai"

urlpatterns = [
    # top (popular) persons
    path('', views.home, name='home'),
    # ajax path
    path('api_get_topPerson/', views.api_get_topPerson),
    path('youtube_search/', views.search_youtube, name='youtube_search'),
]