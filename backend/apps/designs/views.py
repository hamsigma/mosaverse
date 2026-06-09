from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Design
from .serializers import (
    CategorySerializer,
    DesignSerializer,
    DesignListSerializer,
)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryListCreateView(generics.ListCreateAPIView):
    """List semua kategori atau buat kategori baru (admin only)."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detail, update, atau hapus kategori (admin only untuk write)."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class DesignListView(generics.ListAPIView):
    """List semua desain untuk gallery (public)."""
    queryset = Design.objects.filter(
        is_published=True).select_related('category')
    serializer_class = DesignListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category__name']
    ordering_fields = ['created_at', 'title', 'is_featured']
    ordering = ['-created_at']


class DesignDetailView(generics.RetrieveAPIView):
    """Detail desain (public)."""
    queryset = Design.objects.filter(
        is_published=True).select_related('category')
    serializer_class = DesignSerializer
    lookup_field = 'pk'


@method_decorator(csrf_exempt, name='dispatch')
class DesignCreateView(generics.CreateAPIView):
    """Buat desain baru (admin only)."""
    queryset = Design.objects.all()
    serializer_class = DesignSerializer
    permission_classes = [permissions.IsAdminUser]


@method_decorator(csrf_exempt, name='dispatch')
class DesignUpdateView(generics.UpdateAPIView):
    """Update desain (admin only)."""
    queryset = Design.objects.all()
    serializer_class = DesignSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'


@method_decorator(csrf_exempt, name='dispatch')
class DesignDeleteView(generics.DestroyAPIView):
    """Hapus desain (admin only)."""
    queryset = Design.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'
