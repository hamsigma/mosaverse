from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from apps.designs.models import Design, Category
from apps.designs.serializers import DesignListSerializer


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    """Dashboard statistics untuk admin."""
    total_designs = Design.objects.count()
    total_categories = Category.objects.count()
    featured_designs = Design.objects.filter(is_featured=True).count()
    published_designs = Design.objects.filter(is_published=True).count()

    # Recent designs (last 10)
    recent = Design.objects.select_related('category')[:10]
    recent_serializer = DesignListSerializer(
        recent, many=True, context={'request': request})

    return Response({
        'stats': {
            'total_designs': total_designs,
            'total_categories': total_categories,
            'featured_designs': featured_designs,
            'published_designs': published_designs,
        },
        'recent_designs': recent_serializer.data
    })
