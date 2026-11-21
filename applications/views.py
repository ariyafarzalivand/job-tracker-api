from rest_framework import permissions, viewsets

from .models import JobApplication
from .serializers import JobApplicationSerializer


class JobApplicationViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for the logged-in user's job applications."""

    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only the current user's applications, so nobody can
        # read, edit or delete another user's data.
        return JobApplication.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Set the owner on the server instead of trusting the client.
        serializer.save(owner=self.request.user)
