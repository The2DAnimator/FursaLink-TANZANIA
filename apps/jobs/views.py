from django_filters import rest_framework as df
from rest_framework import decorators, viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.core.permissions import IsOwnerOrReadOnly
from apps.jobs.models import Job, JobApplication
from apps.jobs.serializers import JobApplicationSerializer, JobSerializer


class JobFilter(df.FilterSet):
    min_salary = df.NumberFilter(field_name="salary_min", lookup_expr="gte")

    class Meta:
        model = Job
        fields = ("type", "category", "region", "is_active", "business")


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related("posted_by", "business", "category", "region")
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_class = JobFilter
    search_fields = ("title", "company", "description", "location")
    ordering_fields = ("created_at", "deadline", "salary_max")

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def apply(self, request, pk=None):
        job = self.get_object()
        serializer = JobApplicationSerializer(data={**request.data, "job": job.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(applicant=request.user, job=job)
        return Response(serializer.data, status=201)


class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ("job", "status")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return JobApplication.objects.none()
        user = self.request.user
        qs = JobApplication.objects.select_related("job", "applicant")
        if user.is_super_admin or user.is_staff:
            return qs
        # Applicants see their own applications; employers see apps to their jobs.
        return qs.filter(applicant=user) | qs.filter(job__posted_by=user)

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)
