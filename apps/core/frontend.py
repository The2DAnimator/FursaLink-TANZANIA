"""Server-rendered page views. Data is loaded client-side via the REST API."""
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "pages/home.html"


class BusinessListView(TemplateView):
    template_name = "pages/businesses.html"


class BusinessDetailView(TemplateView):
    template_name = "pages/business_detail.html"


class ProductListView(TemplateView):
    template_name = "pages/products.html"


class OpportunityListView(TemplateView):
    template_name = "pages/opportunities.html"


class TenderListView(TemplateView):
    template_name = "pages/tenders.html"


class JobListView(TemplateView):
    template_name = "pages/jobs.html"


class MarketPriceView(TemplateView):
    template_name = "pages/market_prices.html"


class LoginView(TemplateView):
    template_name = "pages/login.html"


class RegisterView(TemplateView):
    template_name = "pages/register.html"


class DashboardView(TemplateView):
    template_name = "pages/dashboard.html"
