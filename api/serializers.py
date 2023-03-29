from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from accounts.models import CustomUser as User, ContactBook
from chatrooms.models import Chatroom, Message


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'first_name', 'last_name', 'email', 'bio',
            'birthdate', 'last_login', 'date_joined',
        ]
        read_only = ['bio', 'last_login', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self, **kwargs):
        if self.validated_data.get('password') is not None:
            self.validated_data['password'] = make_password(self.validated_data['password'])
        return super().save(**kwargs)


class ContactBookSerializer(serializers.ModelSerializer):
    contacts = serializers.HyperlinkedRelatedField(
        many = True,
        read_only = True,
        view_name = 'api:user-detail',
    )
    book_owner = serializers.HyperlinkedRelatedField(
        read_only = True,
        view_name = 'api:user-detail',
    )
    book_owner_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ContactBook
        fields = ['id', 'book_owner', 'book_owner_id', 'contacts']


class MessageSerializer(serializers.ModelSerializer):
    chatroom = serializers.HyperlinkedRelatedField(
        read_only = True,
        view_name = 'api:chatroom-detail',
    )
    sender = serializers.HyperlinkedRelatedField(
        read_only = True,
        view_name = 'api:user-detail',
    )
    chatroom_id = serializers.IntegerField(write_only=True)
    sender_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'chatroom', 'chatroom_id', 'sender', 'sender_id', 'body', 'datetime',
        ]
        extra_kwargs = {
            'datetime': {'read_only': True}
        }


class ChatroomSerializer(serializers.ModelSerializer):
    participants = serializers.HyperlinkedRelatedField(
        many = True,
        read_only = True,
        view_name = 'api:user-detail',
    )
    admins = serializers.HyperlinkedRelatedField(
        many = True,
        read_only = True,
        view_name = 'api:user-detail',
    )

    class Meta:
        model = Chatroom
        fields = [
            'id', 'name', 'description', 'creation_date', 'public',
            'min_age_required', 'participants', 'admins',
        ]
        read_only = ['creation_date']


class ChatroomMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'chatroom', 'sender', 'body']
