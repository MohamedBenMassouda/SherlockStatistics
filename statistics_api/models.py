from django.db import models
from django.utils import timezone
from users.models import User


class Feature(models.Model):
    """
    Track feature usage and performance
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=100)
    creation_date = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class UserInteraction(models.Model):
    """
    Track detailed user interactions with the application
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    interaction_type = models.CharField(
        max_length=50,
        choices=[
            ("click", "Click"),
            ("hover", "Hover"),
            ("focus", "Focus"),
            ("scroll", "Scroll"),
        ],
    )
    timestamp = models.DateTimeField(default=timezone.now)
    duration = models.IntegerField(help_text="Interaction duration in seconds")
    additional_metadata = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "feature", "timestamp"]),
        ]


class UserFeedback(models.Model):
    """
    Store and analyze user feedback
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    rating = models.DecimalField(decimal_places=1, max_digits=2)
    feedback_text = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["category", "rating"]),
        ]
