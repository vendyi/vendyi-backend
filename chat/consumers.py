import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, ChatRoom
from django.utils import timezone
from accounts.models import UserProfile
from channels.db import database_sync_to_async
class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_or_create_user_profile(self, user_id):
        user_profile, created = UserProfile.objects.get_or_create(user_id=user_id)
        user_profile.is_online = True
        user_profile.last_active = timezone.now()
        user_profile.save()
        return user_profile
    
    @database_sync_to_async
    def get_or_create_user_profile_offline(self, user_id):
        user_profile, created = UserProfile.objects.get_or_create(user_id=user_id)
        user_profile.is_online = False
        user_profile.last_active = timezone.now()
        user_profile.save()
        return user_profile
    
    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            message.read = True
            message.save()
            return True
        except Message.DoesNotExist:
            return False
    
    @database_sync_to_async
    def mark_message_as_delivered(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            message.delivered = True
            message.save()
            return True
        except Message.DoesNotExist:
            return False

    async def connect(self):
        self.user = self.scope.get('user')
        self.room_group_name = self.scope['url_route']['kwargs']['room_name']
        user_profile = await self.get_or_create_user_profile(self.user.id)
        
        if self.user.is_anonymous:
            await self.close()
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope['user']
        user_profile = await self.get_or_create_user_profile_offline(user.id)
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message_type = text_data_json.get('type')
        if message_type == 'read':
            message_id = text_data_json.get('message_id')
            if await self.mark_message_as_read(message_id):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message.read',
                        'message_id': message_id,
                    }
                )
        elif message_type == 'delivered':
            message_id = text_data_json.get('message_id')
            if await self.mark_message_as_delivered(message_id):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message.delivered',
                        'message_id': message_id,
                    }
                )
        elif message_type == 'message':
            chat_room = ChatRoom.objects.get(room_name=self.room_group_name)
            # Save the message to the database
            Message.objects.create(
                chat_room = chat_room,
                sender=self.user,
                receiver_id=self.other_user_id,
                content=message,
            )

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': message,
                }
            )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
    async def message_read(self, event):
        # This method will be called when a 'message.read' message is received.
        # You can add code here to handle the message.
        message_id = event['message_id']
        # Send message to WebSocket
        self.mark_message_as_read(message_id)
        await self.send(text_data=json.dumps({
            'type': 'message.read',
            'message_id': message_id
        }))
    async def message_delivered(self, event):
        # This method will be called when a 'message.delivered' message is received.
        # You can add code here to handle the message.
        message_id = event['message_id']
        # Send message to WebSocket
        self.mark_message_as_delivered(message_id)
        await self.send(text_data=json.dumps({
            'type': 'message.delivered',
            'message_id': message_id
        }))
