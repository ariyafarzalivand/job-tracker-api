from rest_framework import permissions, viewsets

from .models import JobApplication
from .serializers import JobApplicationSerializer


class JobApplicationViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for the logged-in user's job applications."""

    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Exact match filter: /api/applications/?status=interview
    filterset_fields = ["status"]
    # Text search over these fields: /api/applications/?search=siemens
    search_fields = ["company", "position", "notes"]
    # Sorting: /api/applications/?ordering=-applied_date
    ordering_fields = ["applied_date", "company", "created_at"]

    def get_queryset(self):
        # Return only the current user's applications, so nobody can
        # read, edit or delete another user's data. Filters, search and
        # sorting are applied on top of this queryset, so they can never
        # reach other users' records.
        return JobApplication.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Set the owner on the server instead of trusting the client.
        serializer.save(owner=self.request.user)
