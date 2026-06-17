from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.matching.engine import Candidate, rank, spam_score
from apps.opportunities.models import Opportunity
from apps.opportunities.serializers import OpportunitySerializer
from apps.products.models import Product
from apps.products.serializers import ProductSerializer


def _product_text(p: Product) -> str:
    return " ".join(filter(None, [
        p.name,
        p.description,
        getattr(p.category, "name", None),
        getattr(p.location, "name", str(p.location) if p.location else None),
    ]))


def _opportunity_text(o: Opportunity) -> str:
    return " ".join(filter(None, [
        o.title,
        o.description,
        getattr(o, "industry", None),
        getattr(o, "location", None),
    ]))


class RecommendProductsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter("q", str, required=True)],
        responses=OpenApiTypes.OBJECT,
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response({"detail": "q is required"}, status=400)

        products = Product.objects.filter(is_active=True)[:500]

        candidates = [
            Candidate(p.id, _product_text(p))
            for p in products
        ]

        ranked = rank(query, candidates)
        by_id = {p.id: p for p in products}

        return Response([
            {
                "score": round(score, 3),
                "product": ProductSerializer(by_id[pid]).data,
            }
            for pid, score in ranked
        ])


class RecommendOpportunitiesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter("q", str, required=True)],
        responses=OpenApiTypes.OBJECT,
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response({"detail": "q is required"}, status=400)

        opps = Opportunity.objects.filter(
            status=Opportunity.Status.OPEN
        )[:500]

        candidates = [
            Candidate(o.id, _opportunity_text(o))
            for o in opps
        ]

        ranked = rank(query, candidates)
        by_id = {o.id: o for o in opps}

        return Response([
            {
                "score": round(score, 3),
                "opportunity": OpportunitySerializer(by_id[oid]).data,
            }
            for oid, score in ranked
        ])


class MatchSellersView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("q", str, required=True),
            OpenApiParameter("region", int, required=False),
            OpenApiParameter("category", int, required=False),
        ],
        responses=OpenApiTypes.OBJECT,
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response({"detail": "q is required"}, status=400)

        qs = Product.objects.filter(is_active=True)

        region = request.query_params.get("region")
        category = request.query_params.get("category")

        if region:
            qs = qs.filter(region_id=region)
        if category:
            qs = qs.filter(category_id=category)

        products = qs[:500]

        candidates = [
            Candidate(p.id, _product_text(p))
            for p in products
        ]

        ranked = rank(query, candidates)
        by_id = {p.id: p for p in products}

        return Response([
            {
                "score": round(score, 3),
                "seller": getattr(by_id[pid].seller, "full_name", "Unknown"),
                "product": ProductSerializer(by_id[pid]).data,
            }
            for pid, score in ranked
        ])


class SpamCheckView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OpenApiTypes.OBJECT, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        text = request.data.get("text", "")
        score = spam_score(text)

        return Response({
            "spam_score": score,
            "is_spam": score >= 0.5,
        })
