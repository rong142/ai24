from django.urls import path
from . import views

app_name="app_user_keyword_ai"

urlpatterns = [
    # the first way:
    path('', views.home, name='home'),
    path('api_get_top_userkey/', views.api_get_top_userkey),
    path('api_get_userkey_llm_report/', views.api_get_userkey_llm_report, name='api_get_userkey_llm_report'),

]
