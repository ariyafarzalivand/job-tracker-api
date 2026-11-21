from rest_framework import serializers

from .models import JobApplication


class JobApplicationSerializer(serializers.ModelSerializer):
    """Converts JobApplication objects to and from JSON."""

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "owner",
            "company",
            "position",
            "status",
            "job_url",
            "applied_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        # The owner is taken from the logged-in user on the server side.
        # If clients could set it, they could create applications
        # in other users' accounts.
        read_only_fields = ["id", "owner", "created_at", "updated_at"]
