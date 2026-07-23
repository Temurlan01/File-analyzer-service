from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
    SpectacularSwaggerView )
from analyzer.views import (
    StartDownloadView, FileListView, CalculateStatsView,
    ResetProgressView, ResetThrottlingView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Главная страница (UI)
    path('', TemplateView.as_view(template_name='analyzer/index.html'), name='home'),

    # API Эндпоинты
    path('api/start-download/', StartDownloadView.as_view(), name='start-download'),
    path('api/files/', FileListView.as_view(), name='file-list'),
    path('api/calculate/', CalculateStatsView.as_view(), name='calculate-stats'),

    # Admin Эндпоинты
    path('api/admin/candidates/<str:candidate_id>/progress/', ResetProgressView.as_view(), name='reset-progress'),
    path('api/admin/clients/<str:client_ip>/throttling/', ResetThrottlingView.as_view(), name='reset-throttling'),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
