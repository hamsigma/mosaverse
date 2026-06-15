from rest_framework import serializers
from .models import Category, Design, Portfolio, PortfolioImage
from .validators import validate_image_file, sanitize_string


def _get_image_url(obj, context):
    """Build absolute URL for a design's image field."""
    request = context.get('request')
    if obj.image and request:
        return request.build_absolute_uri(obj.image.url)
    return None


class CategorySerializer(serializers.ModelSerializer):
    design_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description',
                  'design_count', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_design_count(self, obj):
        return obj.designs.count()

    def validate_name(self, value):
        value = sanitize_string(value, max_length=100)
        if not value:
            raise serializers.ValidationError('Category name cannot be empty.')
        if len(value) < 2:
            raise serializers.ValidationError(
                'Category name must be at least 2 characters.')
        return value

    def validate_description(self, value):
        return sanitize_string(value, max_length=500)


class DesignSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    image = serializers.ImageField(
        required=False, allow_null=True,
        validators=[validate_image_file]
    )
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Design
        fields = [
            'id', 'title', 'slug', 'description', 'image', 'image_url',
            'category', 'category_id', 'is_featured', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        return _get_image_url(obj, self.context)

    def validate_title(self, value):
        value = sanitize_string(value, max_length=200)
        if not value:
            raise serializers.ValidationError('Title cannot be empty.')
        if len(value) < 3:
            raise serializers.ValidationError(
                'Title must be at least 3 characters.')
        return value

    def validate_description(self, value):
        return sanitize_string(value, max_length=2000)

    def validate_image(self, value):
        if value:
            validate_image_file(value)
        elif self.instance is None:
            # Creating new design — image is required
            raise serializers.ValidationError('Image is required for new designs.')
        return value


class DesignListSerializer(serializers.ModelSerializer):
    """Serializer ringan untuk list gallery."""
    category_name = serializers.CharField(
        source='category.name', read_only=True, default='')
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Design
        fields = ['id', 'title', 'slug', 'image', 'image_url',
                  'category_name', 'is_featured', 'is_published', 'created_at']

    def get_image_url(self, obj):
        return _get_image_url(obj, self.context)


# ─── Portfolio Serializers ───────────────────────────────

class PortfolioImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioImage
        fields = ['id', 'image', 'image_url', 'caption', 'order']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class PortfolioSerializer(serializers.ModelSerializer):
    images = PortfolioImageSerializer(many=True, read_only=True)
    image_count = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['id', 'title', 'description', 'thumbnail', 'thumbnail_url',
                  'order', 'images', 'image_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_image_count(self, obj):
        return obj.images.count()

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None
