from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import F

from .. import settings
from ..authentication.models import CustomUser
from .models import Conversation, Message, Generation
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    GenerationSerializer,
)
from .permissions import HasEnoughTokens
from ..ai import chat


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return ConversationListSerializer
        if self.action == "retrieve":
            return ConversationDetailSerializer
        return ConversationListSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        data["user"] = user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(), HasEnoughTokens()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(conversation__user=user)
        # Optional for limit to a conversation
        conversation_id = self.request.query_params.get("conversation_id", None)
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.validated_data["conversation"]
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        messages = list(
            Message.objects.filter(conversation=conversation)[
                : settings.MEMORY_MESSAGE_COUNT
            ]
        )
        response = chat(messages)
        assistant_message = Message.objects.create(
            role="assistant",
            content=response.response,
            conversation=conversation,
        )

        messages.append(assistant_message)
        assistant_message.save()

        # Add new generation (because each generation has memory that contains some messages)
        gen = Generation.objects.create(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
        gen.messages.set(messages)
        gen.save()

        # Decrement user tokens
        total_tokens = response.usage.output_tokens + response.usage.input_tokens
        CustomUser.objects.filter(id=request.user.id).update(
            tokens=F("tokens") - total_tokens,
        )

        return Response(
            {
                "content": assistant_message.content,
                "created_at": assistant_message.created_at,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        conversation_id = self.request.data.get("conversation")
        conversation = Conversation.objects.get(id=conversation_id)
        serializer.save(conversation=conversation)


class GenerationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Generation.objects.all()
    serializer_class = GenerationSerializer
    permission_classes = [IsAdminUser]
