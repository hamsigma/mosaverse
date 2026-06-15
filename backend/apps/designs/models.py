from django.db import models
from django.utils import timezone
from .validators import validate_image_file


class Category(models.Model):
    """Kategori desain baju."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Design(models.Model):
    """Desain baju yang ditampilkan di galeri."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, default='')
    image = models.ImageField(
        upload_to='designs/%Y/%m/', validators=[validate_image_file])
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='designs'
    )
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Design'
        verbose_name_plural = 'Designs'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Design.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class Portfolio(models.Model):
    """Portfolio collection for Design By Me section."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    thumbnail = models.ImageField(upload_to='portfolio/thumbnails/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text='Display order (lower = first)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class PortfolioImage(models.Model):
    """Individual image within a portfolio collection."""
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='portfolio/images/')
    caption = models.CharField(max_length=200, blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Portfolio Image'
        verbose_name_plural = 'Portfolio Images'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.portfolio.title} - {self.caption or self.image.name}"
