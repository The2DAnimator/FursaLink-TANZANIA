from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.http import JsonResponse

from apps.core import frontend


def health(request):
    return JsonResponse({"status": "ok"})


api_patterns = [
    path("api/v1/", include("config.api_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

frontend_patterns = [
    path("", frontend.HomeView.as_view(), name="home"),
    path("businesses/", frontend.BusinessListView.as_view(), name="businesses"),
    path("businesses/<slug:slug>/", frontend.BusinessDetailView.as_view(), name="business-detail"),
    path("products/", frontend.ProductListView.as_view(), name="products"),
    path("opportunities/", frontend.OpportunityListView.as_view(), name="opportunities"),
    path("tenders/", frontend.TenderListView.as_view(), name="tenders"),
    path("jobs/", frontend.JobListView.as_view(), name="jobs"),
    path("market-prices/", frontend.MarketPriceView.as_view(), name="market-prices"),
    path("login/", frontend.LoginView.as_view(), name="login"),
    path("register/", frontend.RegisterView.as_view(), name="register"),
    path("dashboard/", frontend.DashboardView.as_view(), name="dashboard"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    *api_patterns,
    *frontend_patterns,
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if getattr(settings, "STATICFILES_DIRS", None):
        urlpatterns += static(
            settings.STATIC_URL,
            document_root=settings.STATICFILES_DIRS[0]
        )
