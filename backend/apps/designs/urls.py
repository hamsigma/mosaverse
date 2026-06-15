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

    # Portfolio
    path('portfolio/', views.PortfolioListView.as_view(), name='portfolio-list'),
    path('portfolio/create/', views.PortfolioCreateView.as_view(), name='portfolio-create'),
    path('portfolio/<int:pk>/', views.PortfolioDetailView.as_view(), name='portfolio-detail'),
    path('portfolio/<int:portfolio_pk>/images/', views.PortfolioImageAddView.as_view(), name='portfolio-image-add'),
    path('portfolio/images/<int:pk>/delete/', views.PortfolioImageDeleteView.as_view(), name='portfolio-image-delete'),
]
