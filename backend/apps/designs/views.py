from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes as perm_classes
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Design
from .models import Portfolio, PortfolioImage
from .serializers import CategorySerializer, DesignSerializer, DesignListSerializer
from .serializers import PortfolioSerializer, PortfolioImageSerializer


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
    """List semua desain untuk gallery (public). Admin can see all via ?admin=1."""
    serializer_class = DesignListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category__name']
    ordering_fields = ['created_at', 'title', 'is_featured']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Design.objects.select_related('category')
        # Admin can see all designs (including drafts) via ?admin=1
        if (self.request.query_params.get('admin') == '1'
                and self.request.user.is_authenticated
                and self.request.user.is_staff):
            return qs.all()
        return qs.filter(is_published=True)


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


# ─── Toggle Publish (Admin) ─────────────────────────────

@csrf_exempt
@api_view(['POST'])
@perm_classes([permissions.IsAdminUser])
def toggle_publish(request, pk):
    """Toggle is_published status for a design (admin only)."""
    try:
        design = Design.objects.get(pk=pk)
    except Design.DoesNotExist:
        return Response({'error': 'Design not found.'}, status=status.HTTP_404_NOT_FOUND)

    design.is_published = not design.is_published
    design.save(update_fields=['is_published', 'updated_at'])

    return Response({
        'id': design.id,
        'is_published': design.is_published,
        'message': 'Design approved.' if design.is_published else 'Design set to pending.'
    })


# ─── Portfolio Views ────────────────────────────────────

class PortfolioListView(generics.ListAPIView):
    """List all portfolios (public)."""
    queryset = Portfolio.objects.prefetch_related('images')
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.AllowAny]


class PortfolioCreateView(CsrfExemptMixin, generics.CreateAPIView):
    """Create a new portfolio (admin only)."""
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAdminUser]


class PortfolioDetailView(CsrfExemptMixin, generics.RetrieveUpdateDestroyAPIView):
    """Detail, update, or delete a portfolio (admin only for write)."""
    queryset = Portfolio.objects.prefetch_related('images')
    serializer_class = PortfolioSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class PortfolioImageAddView(CsrfExemptMixin, generics.CreateAPIView):
    """Add an image to a portfolio (admin only)."""
    serializer_class = PortfolioImageSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        portfolio = Portfolio.objects.get(pk=self.kwargs['portfolio_pk'])
        serializer.save(portfolio=portfolio)


class PortfolioImageDeleteView(CsrfExemptMixin, generics.DestroyAPIView):
    """Delete an image from a portfolio (admin only)."""
    queryset = PortfolioImage.objects.all()
    permission_classes = [permissions.IsAdminUser]
