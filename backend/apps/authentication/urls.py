from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('csrf/', views.get_csrf_token_view, name='csrf'),
    path('me/', views.me_view, name='me'),
]
