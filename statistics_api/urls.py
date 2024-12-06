from django.urls import path
from statistics_api import views
from statistics_api.views import UserInteractionStatisticsView

app_name = 'statistics_api'

urlpatterns = [
    path("", UserInteractionStatisticsView.as_view(), name='user_interaction_statistics'),
    path("bulk-create/", views.BulkCreateUserInteractionView.as_view(), name='bulk_create_user_interaction'),
    path("interactions/", views.UserInteractionStatisticsView.as_view(), name='user_interaction'),
    path("user/<int:user_id>/", views.UserInteractionByUser.as_view(), name='user_interaction_by_user'),
    # path("features/", views.FeaturesView.as_view(), name='features'),
    path("feedback/", views.CreateUserFeedbackView.as_view(), name='create_feedback'),
    path("feedback/analytics/", views.UserFeedbackAnalyticsView.as_view(), name='feedback_analytics'),
]