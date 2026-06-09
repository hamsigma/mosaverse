from rest_framework import generics, permissions, filters
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Design
from .serializers import CategorySerializer, DesignSerializer, DesignListSerializer


class CsrfExemptMixin:
    """Mixin to apply csrf_exempt to class-based views."""

    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return csrf_exempt(view)


# ─── Category Views ─────────────────────────────────────

class CategoryListCreateView(CsrfExemptMixin, generics.ListCreateAPIView):
    """List semua kategori atau buat kategori baru (admin only)."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class CategoryDetailView(CsrfExemptMixin, generics.RetrieveUpdateDestroyAPIView):
    """Detail, update, atau hapus kategori (admin only untuk write)."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


# ─── Design Views (Public) ─────────────────────────────

class DesignListView(generics.ListAPIView):
    """List semua desain untuk gallery (public)."""
    queryset = Design.objects.filter(is_published=True).select_related('category')
    serializer_class = DesignListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category__name']
    ordering_fields = ['created_at', 'title', 'is_featured']
    ordering = ['-created_at']


class DesignDetailView(generics.RetrieveAPIView):
    """Detail desain (public)."""
    queryset = Design.objects.filter(is_published=True).select_related('category')
    serializer_class = DesignSerializer
    lookup_field = 'pk'


# ─── Design Views (Admin) ──────────────────────────────

class DesignCreateView(CsrfExemptMixin, generics.CreateAPIView):
    """Buat desain baru (admin only)."""
    queryset = Design.objects.all()
    serializer_class = DesignSerializer
    permission_classes = [permissions.IsAdminUser]


class DesignUpdateView(CsrfExemptMixin, generics.UpdateAPIView):
    """Update desain (admin only)."""
    queryset = Design.objects.all()
    serializer_class = DesignSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'


class DesignDeleteView(CsrfExemptMixin, generics.DestroyAPIView):
    """Hapus desain (admin only)."""
    queryset = Design.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'
