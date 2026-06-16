from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API Endpoints
    path('api/', include('apps.authentication.urls', namespace='authentication')),
    path('api/', include('apps.designs.urls', namespace='designs')),
    path('api/ai/', include('apps.ai.urls', namespace='ai')),
    path('api/dashboard/', include('apps.dashboard.urls', namespace='dashboard')),

    # DRF Auth (for browsable API)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

# Always serve media files via Django's serve view in production (needed for Vercel /tmp storage)
from django.views.static import serve
from django.urls import re_path
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]
