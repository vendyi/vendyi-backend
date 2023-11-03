from django.db import models

class ChatRoom(models.Model):
    sender = models.ForeignKey('accounts.User', related_name='sender', on_delete=models.CASCADE, blank=True, null=True)
    receiver = models.ForeignKey('accounts.User', related_name='receiver', on_delete=models.CASCADE, blank=True, null=True)
    room_name = models.CharField(max_length=250)
    
    def __str__(self):
        return self.room_name
# Create your models here.
class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey('accounts.User', related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    receiver = models.ForeignKey('accounts.User', related_name='received_messages', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    file = models.FileField(upload_to='messages/', blank=True, null=True)  # Add this line
    reply_to = models.ForeignKey('self', related_name='replies', on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return self.content if self.content else f'File: {self.file.name}'
