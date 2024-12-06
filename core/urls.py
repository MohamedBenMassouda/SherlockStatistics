from django.urls import path, include
from drf_spectacular.views import SpectacularRedocView, SpectacularSwaggerView, SpectacularAPIView

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc UI
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path("auth/", include("auth.urls", namespace="auth")),
    path("users/", include("users.urls", namespace="users")),
    path("stats/", include("statistics_api.urls", namespace="stats")),
]
