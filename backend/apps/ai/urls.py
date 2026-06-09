from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('search/', views.ai_search, name='search'),
    path('generate-description/', views.generate_description, name='generate-description'),
    path('generate-category/', views.generate_category, name='generate-category'),
]
