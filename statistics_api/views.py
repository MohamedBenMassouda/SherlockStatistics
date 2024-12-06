from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta

from .models import UserInteraction, UserFeedback
from .serializer import UserInteractionCreateSerializer, UserFeedbackSerializer, \
    UserFeedbackCreateSerializer
from users.models import User


class UserInteractionStatisticsView(APIView):
    """
    Provides comprehensive analytics on user interactions across the platform.

    This view offers in-depth statistics about user interactions, including:
    - Total number of interactions
    - Interactions in the last 30 days
    - Breakdown of interaction types
    - Performance metrics for different features
    - Top active users

    Permissions:
    - Restricted to admin users only
    - Requires IsAdminUser permission

    Caching:
    - Statistics are cached for 1 hour to reduce database load
    - Cache key is dynamically generated to ensure fresh data
    """
    permission_classes = [IsAdminUser]

    @extend_schema(
        description="Retrieve comprehensive user interaction statistics for the last 30 days.",
        responses={
            200: {
                'description': 'Detailed user interaction statistics.',
                'content': {
                    'application/json': {
                        'example': {
                            'total_interactions': 1000,
                            'interactions_last_30_days': 500,
                            'interaction_type_breakdown': [
                                {'interaction_type': 'view', 'count': 300},
                                {'interaction_type': 'click', 'count': 200}
                            ],
                            'feature_interaction_stats': [
                                {
                                    'feature__name': 'Dashboard',
                                    'interaction_count': 250,
                                    'avg_duration': 45.5
                                }
                            ],
                            'top_10_active_users': [
                                {'user__username': 'johndoe', 'interaction_count': 50}
                            ]
                        }
                    }
                }
            }
        },
        tags=['User Interactions']
    )
    def get(self, request):
        """
        Retrieves and aggregates user interaction statistics.

        Generates a comprehensive report including:
        - Total interaction count
        - Interactions in the last 30 days
        - Interaction type distribution
        - Feature-level interaction metrics
        - Most active users

        Returns:
        - JSON response with detailed interaction statistics

        Caching Strategy:
        - Results are cached for 1 hour to improve performance
        - Cache is invalidated when new interactions are recorded
        """
        # Generate a unique cache key based on current time (hourly)
        cache_key = f'user_interaction_stats_{timezone.now().strftime("%Y%m%d%H")}'

        # Try to retrieve cached results
        cached_stats = cache.get(cache_key)
        if cached_stats:
            return Response(cached_stats)

        # Time-based filters
        last_30_days = timezone.now() - timedelta(days=30)

        # Overall interaction statistics
        total_interactions = UserInteraction.objects.count()
        interactions_last_30_days = UserInteraction.objects.filter(timestamp__gte=last_30_days)

        # Interaction type breakdown
        interaction_type_breakdown = interactions_last_30_days.values('interaction_type').annotate(
            count=Count('id')
        )

        # Feature interaction statistics
        feature_interaction_stats = interactions_last_30_days.values('feature__name').annotate(
            interaction_count=Count('id'),
            avg_duration=Avg('duration')
        ).order_by('-interaction_count')

        # User interaction statistics
        user_interaction_stats = interactions_last_30_days.values('user__username').annotate(
            interaction_count=Count('id')
        ).order_by('-interaction_count')[:10]

        # Prepare response data
        stats_data = {
            'total_interactions': total_interactions,
            'interactions_last_30_days': interactions_last_30_days.count(),
            'interaction_type_breakdown': list(interaction_type_breakdown),
            'feature_interaction_stats': list(feature_interaction_stats),
            'top_10_active_users': list(user_interaction_stats)
        }

        # Cache the results for 1 hour
        cache.set(cache_key, stats_data, timeout=3600)

        return Response(stats_data)


class BulkCreateUserInteractionView(APIView):
    """
    Enables bulk creation of user interactions in a single request.

    Key Features:
    - Supports creating multiple interactions simultaneously
    - Validates each interaction before bulk insertion
    - Provides detailed error reporting
    - Automatically associates interactions with the authenticated user

    Permissions:
    - Requires user authentication
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Bulk create multiple user interactions in a single request",
        request=UserInteractionCreateSerializer(many=True),
        responses={
            201: OpenApiResponse(
                description="Interactions successfully created",
                response=dict,
                examples=[
                    OpenApiExample(
                        'Successful Creation',
                        value={"message": "5 interactions created successfully"}
                    )
                ]
            ),
            400: OpenApiResponse(description="Invalid input data")
        },
        tags=['User Interactions']
    )
    def post(self, request):
        """
        Process bulk creation of user interactions.

        Workflow:
        1. Validate incoming interaction data
        2. Associate interactions with current user
        3. Bulk save valid interactions
        4. Invalidate relevant caches

        Args:
            request: HTTP request containing list of interaction objects

        Returns:
            Response with success message or validation errors
        """
        # Validate the incoming data
        serializer = UserInteractionCreateSerializer(
            data=request.data,
            many=True,
            context={'user': request.user}
        )

        if serializer.is_valid():
            # Save all interactions
            serializer.save()

            # Invalidate interaction statistics cache
            cache.delete_pattern('user_interaction_stats_*')

            return Response(
                {"message": f"{len(serializer.validated_data)} interactions created successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInteractionByUser(APIView):
    """
    Retrieve and filter user interactions for administrative purposes.

    Provides flexible querying of user interactions with multiple filtering options.

    Permissions:
    - Restricted to admin users
    """
    permission_classes = [IsAdminUser]

    @extend_schema(
        description="Retrieve user interactions with advanced filtering",
        parameters=[
            OpenApiParameter(name='type', description='Filter by interaction type', required=False, type=str),
            OpenApiParameter(name='start_date', description='Start date for interactions', required=False, type=str),
            OpenApiParameter(name='end_date', description='End date for interactions', required=False, type=str)
        ]
    )
    def get(self, request, user_id):
        """
        Fetch interactions for a specific user with optional filtering.

        Supports filtering by:
        - Interaction type
        - Date range

        Args:
            request: HTTP request with optional query parameters
            user_id: ID of the user whose interactions are being retrieved

        Returns:
            Filtered list of user interactions
        """
        # Generate a unique cache key for this specific query
        cache_key = f'user_interactions_{user_id}_{hash(frozenset(request.query_params.items()))}'

        # Try to retrieve cached results
        cached_interactions = cache.get(cache_key)
        if cached_interactions:
            return Response(cached_interactions)

        try:
            # Filter interactions by user
            interactions = UserInteraction.objects.filter(user_id=user_id)

            # Optional query parameters for filtering
            interaction_type = request.query_params.get('type')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')

            # Apply filters
            if interaction_type:
                interactions = interactions.filter(interaction_type=interaction_type)

            if start_date:
                interactions = interactions.filter(timestamp__gte=start_date)

            if end_date:
                interactions = interactions.filter(timestamp__lte=end_date)

            # Serialize interactions
            serializer = UserInteractionCreateSerializer(interactions, many=True)

            # Cache the results for 30 minutes
            cache.set(cache_key, serializer.data, timeout=1800)

            return Response(serializer.data)

        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserFeedbackAnalyticsView(APIView):
    """
    Comprehensive analytics for user feedback.

    Provides insights into user feedback trends, ratings, and recent submissions.

    Permissions:
    - Restricted to admin users
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        Retrieve aggregated user feedback analytics.

        Generates:
        - Summary of feedback by category
        - Average ratings
        - 10 most recent feedback entries

        Caching strategy prevents frequent database hits.

        Returns:
            Comprehensive feedback analytics
        """
        # Generate a cache key
        cache_key = f'feedback_analytics_{timezone.now().strftime("%Y%m%d%H")}'

        # Check cache first
        cached_analytics = cache.get(cache_key)
        if cached_analytics:
            return Response(cached_analytics)

        # Feedback analytics
        feedback_summary = UserFeedback.objects.values('category').annotate(
            total_feedbacks=Count('id'),
            average_rating=Avg('rating')
        )

        # Recent feedback
        recent_feedback = UserFeedback.objects.order_by('-timestamp')[:10]

        # Prepare analytics data
        analytics_data = {
            'feedback_summary': list(feedback_summary),
            'recent_feedback': UserFeedbackSerializer(recent_feedback, many=True).data
        }

        # Cache for 1 hour
        cache.set(cache_key, analytics_data, timeout=3600)

        return Response(analytics_data)


class CreateUserFeedbackView(generics.CreateAPIView):
    """
    Allow authenticated users to submit feedback.

    Workflow:
    - Validates user feedback
    - Associates feedback with authenticated user
    - Handles feedback creation
    """
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Submit user feedback.

        Process:
        1. Authenticate the user
        2. Validate feedback data
        3. Save feedback
        4. Invalidate feedback analytics cache

        Returns:
            Created feedback object
        """
        user = request.user
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)

        # Save the feedback
        self.perform_create(serializer)

        # Invalidate feedback analytics cache
        cache.delete_pattern('feedback_analytics_*')

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAdminUser()]

        return super().get_permissions()
