from statistics_api.models import Feature, UserFeedback, UserInteraction
from rest_framework import serializers


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = "__all__"


class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = "__all__"


class UserInteractionCreateSerializer(serializers.ModelSerializer):
    interaction_type = serializers.ChoiceField(
        choices=[
            ("click", "Click"),
            ("hover", "Hover"),
            ("focus", "Focus"),
            ("scroll", "Scroll"),
        ]
    )
    feature_name = serializers.CharField(write_only=True)

    class Meta:
        model = UserInteraction
        fields = ["interaction_type", "feature_name", "duration", "additional_metadata"]
        read_only_fields = ["timestamp"]

    def validate(self, attrs):
        user = self.context["user"]

        if not user.is_authenticated:
            return serializers.ValidationError("User is not authenticated")

        if not Feature.objects.filter(name=attrs["feature_name"]).exists():
            raise serializers.ValidationError("Feature does not exist")

        return attrs

    def create(self, validated_data):
        user = self.context["user"]
        feature_name = validated_data.pop("feature_name")
        feature = Feature.objects.get(name=feature_name)

        user_interaction = UserInteraction.objects.create(
            **validated_data, feature=feature, user=user
        )
        return user_interaction


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = "__all__"


class UserFeedbackCreateSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    rating = serializers.DecimalField(max_digits=2, decimal_places=1)
    feedback_text = serializers.CharField(required=False)

    class Meta:
        model = UserFeedback
        fields = ["category", "rating", "feedback_text"]
        read_only_fields = ["timestamp"]

    def create(self, validated_data):
        user = self.context["user"]
        user_feedback = UserFeedback.objects.create(**validated_data, user=user)
        return user_feedback