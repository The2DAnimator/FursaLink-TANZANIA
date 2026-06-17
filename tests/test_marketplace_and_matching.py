import pytest

from apps.matching.engine import Candidate, rank, spam_score
from apps.products.models import Product

pytestmark = pytest.mark.django_db


def test_product_creation_sets_seller_and_slug(auth_client):
    client, user = auth_client(role="seller")
    resp = client.post(
        "/api/v1/products/",
        {"name": "Fresh Maize", "price": "1000.00", "quantity": 10},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["seller"] == user.id
    assert resp.data["slug"] == "fresh-maize"
    assert resp.data["in_stock"] is True


def test_product_price_filter(api, make_user):
    seller = make_user(email="s@example.com", role="seller")
    Product.objects.create(seller=seller, name="Cheap", price=100, quantity=1)
    Product.objects.create(seller=seller, name="Pricey", price=10000, quantity=1)
    resp = api.get("/api/v1/products/?min_price=5000")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.data["results"]]
    assert names == ["Pricey"]


def test_rank_orders_by_relevance():
    candidates = [
        Candidate(1, "maize grain cereal bulk"),
        Candidate(2, "steel construction rods"),
        Candidate(3, "fresh maize from farm"),
    ]
    ranked = rank("maize", candidates)
    assert ranked[0][0] in (1, 3)
    assert all(score > 0 for _, score in ranked)


def test_spam_score_detects_spam():
    assert spam_score("Click here to win FREE MONEY now!!!") >= 0.3
    assert spam_score("Quality maize available in bulk") < 0.3


def test_match_products_endpoint(auth_client):
    client, user = auth_client(role="buyer")
    from apps.accounts.models import User

    seller = User.objects.create_user("seller9@example.com", "password123", role=User.Role.SELLER)
    Product.objects.create(seller=seller, name="Maize Premium", description="bulk maize", price=500, quantity=5)
    resp = client.get("/api/v1/match/products/?q=maize")
    assert resp.status_code == 200
    assert len(resp.data) >= 1
