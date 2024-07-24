from rest_framework import serializers
from .models import Conversation, Message, Generation
from ..authentication.serializers import CustomUserSerializer


class MessageSerializer(serializers.ModelSerializer):
    # user = serializers.SerializerMethodField()
    conversation = serializers.UUIDField()

    class Meta:
        model = Message
        fields = ["id", "conversation", "role", "content", "created_at"]

    def validate_conversation(self, value):
        try:
            return Conversation.objects.get(id=value)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("Conversation does not exist")

    # def get_user(self, obj):
    #     return CustomUserSerializer(obj.conversation.user).data


class ConversationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "user", "created_at", "updated_at", "reset"]


class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "user", "created_at", "updated_at", "reset", "messages"]


class GenerationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Generation
        fields = [
            "id",
            "messages",
            "input_tokens",
            "output_tokens",
            "created_at",
        ]
