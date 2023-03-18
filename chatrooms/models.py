from django.db import models

from accounts.models import CustomUser as User


class Chatroom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=1000, blank=True, null=True, default='')
    creation_date = models.DateField(auto_now=True)
    public = models.BooleanField(default=True)
    min_age_required = models.IntegerField(default=13)
    topics = models.ManyToManyField('chatrooms.Topic', related_name='chatrooms')
    participants = models.ManyToManyField(User, related_name='chatrooms')

    def __str__(self) -> str:
        return self.name


class ChatroomMessage(models.Model):
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='messages')
    body = models.CharField(max_length=1000)

    def __str__(self):
        return f'{self.sender.username}: {self.body[:100]}'


class Topic(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name
