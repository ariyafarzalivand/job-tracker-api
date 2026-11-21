from django.conf import settings
from django.db import models


class JobApplication(models.Model):
    """A single job application submitted by a user."""

    class Status(models.TextChoices):
        # Restricting status to fixed values keeps the data clean
        # and makes filtering by status reliable.
        APPLIED = "applied", "Applied"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"
        REJECTED = "rejected", "Rejected"

    # Each application belongs to one user. This lets the API return
    # only the requesting user's data. CASCADE removes the applications
    # if the user account is deleted.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications",
    )
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPLIED,
    )
    job_url = models.URLField(blank=True)
    applied_date = models.DateField()
    notes = models.TextField(blank=True)

    # Set automatically by Django, so they are never entered by hand.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Newest applications first, which is what a user usually wants to see.
        ordering = ["-applied_date"]

    def __str__(self):
        return f"{self.position} at {self.company}"
