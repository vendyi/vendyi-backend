# chat/serializers.py

from rest_framework import serializers
from .models import Message,ChatRoom

class MessageSerializer(serializers.ModelSerializer):
    chat_room = serializers.StringRelatedField()
    reply_to = serializers.PrimaryKeyRelatedField(read_only=True)  # Add this line
    original_message = serializers.SerializerMethodField()  # Add this line

    class Meta:
        model = Message
        fields = '__all__'
        extra_fields = ['original_message']  # Add this li0ne

    def get_original_message(self, obj):
        if obj.reply_to is not None:
            return MessageSerializer(obj.reply_to).data
        return None

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content', 'receiver', 'reply_to', 'file','id']  # Add 'file' to the list of fields

class ChatRoomSerializer(serializers.ModelSerializer):
    most_recent_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'sender', 'receiver', 'most_recent_message']

    def get_most_recent_message(self, obj):
        if obj.messages.exists():
            message = obj.messages.first()
            return MessageSerializer(message).data