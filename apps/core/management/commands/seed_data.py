"""Populate the database with realistic demo data for FursaLink Tanzania.

Usage:
    python manage.py seed_data           # idempotent-ish demo dataset
    python manage.py seed_data --flush   # clear existing demo data first
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.advertising.models import AdPlan
from apps.businesses.models import Business, Review
from apps.core.models import Category, District, Region
from apps.jobs.models import Job
from apps.leads.models import Lead
from apps.marketprices.models import Market, MarketPrice
from apps.opportunities.models import Opportunity
from apps.products.models import Product
from apps.subscriptions.models import Plan
from apps.tenders.models import Tender

User = get_user_model()

REGIONS = {
    "Dar es Salaam": ["Ilala", "Kinondoni", "Temeke", "Ubungo", "Kigamboni"],
    "Arusha": ["Arusha City", "Meru", "Karatu", "Monduli"],
    "Mwanza": ["Nyamagana", "Ilemela", "Sengerema"],
    "Dodoma": ["Dodoma Urban", "Bahi", "Chamwino"],
    "Mbeya": ["Mbeya City", "Mbarali", "Rungwe"],
    "Kilimanjaro": ["Moshi", "Hai", "Rombo"],
}

BUSINESS_CATEGORIES = ["Agriculture", "Retail", "Manufacturing", "Construction", "Logistics", "ICT", "Hospitality", "Finance"]
PRODUCT_CATEGORIES = ["Grains & Cereals", "Fresh Produce", "Building Materials", "Electronics", "Machinery", "Textiles"]
JOB_CATEGORIES = ["Engineering", "Sales & Marketing", "Finance", "ICT", "Operations", "Agriculture"]

CROPS = ["Maize", "Rice", "Beans", "Coffee", "Cashew nuts", "Sunflower", "Cassava"]
MATERIALS = ["Cement (50kg)", "Steel bar (12mm)", "Sand (ton)", "Bricks (1000)", "Roofing sheet"]


class Command(BaseCommand):
    help = "Seed the database with demo data."

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Delete existing demo data first")

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing demo data...")
            for model in [Lead, Review, Product, Opportunity, Job, MarketPrice, Market, Tender, Business]:
                model.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        random.seed(42)
        regions = self._regions()
        biz_cats = self._categories(BUSINESS_CATEGORIES, Category.Kind.BUSINESS)
        prod_cats = self._categories(PRODUCT_CATEGORIES, Category.Kind.PRODUCT)
        job_cats = self._categories(JOB_CATEGORIES, Category.Kind.JOB)
        self._plans()
        self._ad_plans()
        self._superuser()
        owners = self._users("owner", User.Role.BUSINESS_OWNER, 8)
        sellers = self._users("seller", User.Role.SELLER, 6)
        buyers = self._users("buyer", User.Role.BUYER, 6)
        self._users("jobseeker", User.Role.JOB_SEEKER, 6)

        businesses = self._businesses(owners, biz_cats, regions)
        self._reviews(businesses, buyers)
        self._products(sellers, prod_cats, regions, businesses)
        self._opportunities(owners, regions, businesses)
        self._tenders(regions)
        self._jobs(owners, job_cats, regions, businesses)
        self._market_prices(regions)
        self._leads(businesses, buyers)

        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write("Admin login: admin@fursalink.co.tz / admin12345")
        self.stdout.write("Demo user password for all seeded users: password123")

    # ---- helpers -------------------------------------------------------
    def _regions(self):
        regions = []
        for name, districts in REGIONS.items():
            region, _ = Region.objects.get_or_create(name=name)
            for d in districts:
                District.objects.get_or_create(region=region, name=d)
            regions.append(region)
        return regions

    def _categories(self, names, kind):
        cats = []
        for n in names:
            cat, _ = Category.objects.get_or_create(slug=slugify(f"{kind}-{n}"), defaults={"name": n, "kind": kind})
            cats.append(cat)
        return cats

    def _plans(self):
        data = [
            ("Free", Plan.Tier.FREE, 0, 3, False, False, False, False),
            ("Standard", Plan.Tier.STANDARD, 25000, 25, True, False, False, False),
            ("Premium", Plan.Tier.PREMIUM, 75000, 200, True, True, True, True),
        ]
        for name, tier, price, listings, analytics, leadgen, featured, support in data:
            Plan.objects.get_or_create(tier=tier, defaults={
                "name": name, "price": Decimal(price), "max_listings": listings,
                "has_analytics": analytics, "has_lead_generation": leadgen,
                "featured_placement": featured, "priority_support": support})

    def _ad_plans(self):
        for placement, price in [
            (AdPlan.Placement.FEATURED_LISTING, 15000), (AdPlan.Placement.HOMEPAGE, 50000),
            (AdPlan.Placement.BANNER, 30000), (AdPlan.Placement.SPONSORED_OPPORTUNITY, 20000)]:
            AdPlan.objects.get_or_create(placement=placement, defaults={
                "name": placement.label, "price": Decimal(price)})

    def _superuser(self):
        admin = User.objects.filter(email="admin@fursalink.co.tz").first()
        if not admin:
            admin = User.objects.create_superuser("admin@fursalink.co.tz", "admin12345", first_name="Super", last_name="Admin")
        return admin

    def _users(self, prefix, role, n):
        users = []
        for i in range(n):
            email = f"{prefix}{i+1}@fursalink.co.tz"
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.create_user(email, "password123", role=role, is_verified=True,
                    first_name=prefix.capitalize(), last_name=str(i + 1), phone=f"+2557{random.randint(10000000, 99999999)}")
            users.append(user)
        return users

    def _businesses(self, owners, cats, regions):
        names = ["Kilimo Bora", "Mwanga Traders", "Zanzibar Spices", "Serengeti Logistics", "Uhuru Construction",
                 "Tanzanite ICT", "Bahari Foods", "Kanju Manufacturing", "Safari Hospitality", "Pamoja Finance"]
        businesses = []
        for i, name in enumerate(names):
            region = random.choice(regions)
            biz, _ = Business.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    "owner": random.choice(owners), "name": name, "category": random.choice(cats),
                    "description": f"{name} is a leading Tanzanian enterprise serving {region.name} and beyond.",
                    "region": region, "address": f"{random.randint(1, 200)} Uhuru St, {region.name}",
                    "phone": f"+2556{random.randint(10000000, 99999999)}", "email": f"info@{slugify(name)}.co.tz",
                    "verification_status": random.choice([Business.VerificationStatus.VERIFIED, Business.VerificationStatus.PENDING]),
                    "is_featured": i < 3, "latitude": -6.79 + random.uniform(-2, 2), "longitude": 39.2 + random.uniform(-3, 3),
                    "views_count": random.randint(10, 2000)})
            businesses.append(biz)
        return businesses

    def _reviews(self, businesses, buyers):
        for biz in businesses:
            for user in random.sample(buyers, k=min(3, len(buyers))):
                Review.objects.get_or_create(business=biz, user=user, defaults={
                    "rating": random.randint(3, 5), "comment": "Great service and reliable products."})

    def _products(self, sellers, cats, regions, businesses):
        items = ["Maize 50kg", "Premium Rice", "Cement", "Solar Panel 200W", "Water Pump", "Cotton Fabric",
                 "Sunflower Oil 5L", "Steel Bars", "Cashew Nuts 25kg", "LED TV 32\""]
        for name in items:
            Product.objects.get_or_create(
                slug=slugify(name),
                defaults={"seller": random.choice(sellers), "business": random.choice(businesses),
                    "name": name, "category": random.choice(cats), "description": f"High quality {name} available in bulk.",
                    "price": Decimal(random.randint(5000, 800000)), "quantity": random.randint(0, 500),
                    "region": random.choice(regions), "location": random.choice(regions).name,
                    "views_count": random.randint(0, 500)})

    def _opportunities(self, owners, regions, businesses):
        titles = [
            ("Bulk maize supply needed", Opportunity.Type.SUPPLY, "Agriculture"),
            ("Looking to buy construction cement", Opportunity.Type.BUYER, "Construction"),
            ("Seeking investor for agro-processing", Opportunity.Type.INVESTMENT, "Agriculture"),
            ("Distribution partner for electronics", Opportunity.Type.DISTRIBUTION, "Electronics"),
            ("Joint venture in logistics", Opportunity.Type.PARTNERSHIP, "Logistics"),
            ("Supply of office furniture", Opportunity.Type.SUPPLY, "Retail"),
        ]
        for title, typ, industry in titles:
            Opportunity.objects.get_or_create(
                title=title,
                defaults={"posted_by": random.choice(owners), "business": random.choice(businesses), "type": typ,
                    "description": f"{title}. Serious and verified parties only.", "industry": industry,
                    "region": random.choice(regions), "budget_min": Decimal(random.randint(100000, 1000000)),
                    "budget_max": Decimal(random.randint(1000000, 50000000)),
                    "deadline": timezone.now().date() + timedelta(days=random.randint(10, 90)),
                    "status": Opportunity.Status.OPEN})

    def _tenders(self, regions):
        orgs = ["Ministry of Works", "TANROADS", "World Vision TZ", "CRDB Bank", "Tanesco", "UNICEF Tanzania"]
        for i, org in enumerate(orgs):
            Tender.objects.get_or_create(
                tender_number=f"TZ/{2026}/{1000 + i}", organization=org,
                defaults={"title": f"Procurement notice {i+1} from {org}", "description": "Supply and delivery of goods/services.",
                    "sector": random.choice([Tender.Sector.GOVERNMENT, Tender.Sector.NGO, Tender.Sector.PRIVATE]),
                    "region": random.choice(regions), "closing_date": timezone.now().date() + timedelta(days=random.randint(7, 60))})

    def _jobs(self, owners, cats, regions, businesses):
        roles = ["Sales Manager", "Software Engineer", "Accountant", "Farm Supervisor", "Logistics Officer",
                 "Marketing Intern", "Civil Engineer", "Procurement Officer"]
        for role in roles:
            Job.objects.get_or_create(
                title=role, company=random.choice(businesses).name,
                defaults={"posted_by": random.choice(owners), "category": random.choice(cats),
                    "description": f"We are hiring a {role}. Competitive salary and growth opportunities.",
                    "type": random.choice(list(Job.Type)), "salary_min": Decimal(random.randint(300000, 800000)),
                    "salary_max": Decimal(random.randint(800000, 3000000)), "region": random.choice(regions),
                    "location": random.choice(regions).name, "experience_years": random.randint(0, 8),
                    "deadline": timezone.now().date() + timedelta(days=random.randint(7, 45))})

    def _market_prices(self, regions):
        for region in regions:
            market, _ = Market.objects.get_or_create(name=f"{region.name} Central Market", region=region)
            for product in CROPS + MATERIALS:
                cat = "crops" if product in CROPS else "building_materials"
                base = random.randint(800, 60000)
                for d in range(0, 60, 5):
                    date = timezone.now().date() - timedelta(days=d)
                    price = Decimal(base + random.randint(-base // 10, base // 10))
                    MarketPrice.objects.get_or_create(
                        product=product, market=market, unit="kg" if cat == "crops" else "unit", date=date,
                        defaults={"category": cat, "region": region, "price": price})

    def _leads(self, businesses, buyers):
        for biz in random.sample(businesses, k=min(5, len(businesses))):
            for user in random.sample(buyers, k=2):
                Lead.objects.get_or_create(
                    business=biz, created_by=user,
                    defaults={"type": random.choice(list(Lead.Type)), "contact_name": user.full_name,
                        "message": "I am interested in your products and would like to connect.",
                        "industry": biz.category.name if biz.category else ""})
