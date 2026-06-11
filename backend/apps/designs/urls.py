from django.urls import path
from . import views

app_name = 'designs'

urlpatterns = [
    # Category
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # Design
    path('designs/', views.DesignListView.as_view(), name='design-list'),
    path('designs/<int:pk>/', views.DesignDetailView.as_view(), name='design-detail'),
    path('designs/create/', views.DesignCreateView.as_view(), name='design-create'),
    path('designs/<int:pk>/update/', views.DesignUpdateView.as_view(), name='design-update'),
    path('designs/<int:pk>/delete/', views.DesignDeleteView.as_view(), name='design-delete'),
    path('designs/<int:pk>/toggle-publish/', views.toggle_publish, name='design-toggle-publish'),
]
