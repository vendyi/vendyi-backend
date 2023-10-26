# chat/serializers.py

from rest_framework import serializers
from .models import Message,ChatRoom

class MessageSerializer(serializers.ModelSerializer):
    chat_room = serializers.StringRelatedField()
    class Meta:
        model = Message
        fields = '__all__'

class ChatRoomSerializer(serializers.ModelSerializer):
    most_recent_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'sender', 'receiver', 'most_recent_message']

    def get_most_recent_message(self, obj):
        if obj.messages.exists():
            message = obj.messages.first()
            return MessageSerializer(message).data