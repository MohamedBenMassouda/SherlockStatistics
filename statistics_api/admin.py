from django.contrib import admin

from statistics_api.models import UserInteraction, Feature, UserFeedback


# Register your models here.
@admin.register(UserInteraction)
class UserInteractionsAdmin(admin.ModelAdmin):
    list_display = ("user", "feature__name", "interaction_type", "duration")

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "category", "creation_date")


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "rating", "feedback_text", "timestamp")