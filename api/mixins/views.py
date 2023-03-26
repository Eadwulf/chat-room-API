from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework import status

from accounts.models import CustomUser as User
from chatrooms.models import Chatroom

from api.serializers import (
    UserSerializer,
    MessageSerializer,
    ChatroomMessageSerializer,
)
from api.mixins.helpers import (
    UserMixin,
    MessageMixin,
    ChatroomMixin,
)
from api.mixins.permissions import (
    UserListPermissionsMixin,
    UserDetailPermissionsMixin,
    MessageListPermissionsMixin,
    MessageDetailPermissionsMixin,
    ChatroomListPermissionsMixin,
    ChatroomDetailPermissionsMixin,
    ChatroomMessageListPermissionsMixin,
    ChatroomAdminListPermissionsMixin,
    ChatroomParticipantListPermissionsMixin,
)


class UserListViewMixin(UserListPermissionsMixin, UserMixin):

    def get_queryset(self, queryset=None):
        return super().get_queryset(queryset)


class UserDetailViewMixin(UserDetailPermissionsMixin):
    pass


class MessageListViewMixin(MessageListPermissionsMixin, MessageMixin):

    def get_queryset(self, queryset=None):
        return super().get_queryset(queryset)


class MessageDetailViewMixin(MessageDetailPermissionsMixin):
    pass


class ChatroomListViewMixin(ChatroomListPermissionsMixin, ChatroomMixin):

    def get_queryset(self):
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        """
            Method that creates a Chatroom object and append the user
            in the requets to the 'admins' attribute on the Chatroom object.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self.add_admin(request, serializer)
        self.add_participant(request, serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def add_admin(self, request, serializer):
        admin = request.user
        Chatroom.objects.get(name=serializer.validated_data['name']).admins.add(admin)

    def add_participant(self, request, serializer):
        participant = request.user
        Chatroom.objects.get(name=serializer.validated_data['name']).participants.add(participant)

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class ChatroomDetailViewMixin(ChatroomDetailPermissionsMixin, ChatroomMixin):
    pass


class ChatroomMessageListViewMixin(ChatroomMessageListPermissionsMixin, MessageMixin, ChatroomMixin):

    def list_messages(self, request, *args, **kwargs):
        chatroom = self.get_chatroom_from_request(request)
        serializer = MessageSerializer(
            self.get_queryset(queryset=chatroom.messages.all()),
            many = True,
            context = {'request': request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def send_message(self, request, *args, **kwargs):
        serializer = ChatroomMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chatroom = self.get_chatroom_from_request(request)
        if isinstance(chatroom, Chatroom):
            serializer.validated_data['chatroom'] = chatroom
        if isinstance(request.user, User):
            serializer.validated_data['sender'] = request.user
        serializer.save()
        return self.list_messages(request, *args, **kwargs)


class ChatroomAdminListViewMixin(ChatroomAdminListPermissionsMixin, UserMixin, ChatroomMixin):

    def get_queryset(self, queryset=None):
        return super().get_queryset(queryset)

    def get_admin_from_request(self, request):
        admin_id = request.data.get('id')
        try:
            return User.objects.get(pk=admin_id)
        except User.DoesNotExist:
            return None

    def list_admins(self, request):
        chatroom = self.get_chatroom_from_request(request)
        if isinstance(chatroom, Chatroom):
            serializer = UserSerializer(
                self.get_queryset(queryset=chatroom.admins.all()),
                many = True,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Bad Request': 'Object not found!'}, status=status.HTTP_404_NOT_FOUND)

    def perform_add_or_delete_admin(self, request):
        chatroom = self.get_chatroom_from_request(request)
        if not isinstance(chatroom, Chatroom):
            return Response({'Bad Request': f'Chatroom not found!'}, status=status.HTTP_404_NOT_FOUND)
        admin = self.get_admin_from_request(request)
        if not isinstance(admin, User):
            return Response({'Bad Request': f'User not found!'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            if not chatroom.participants.filter(pk=admin.pk).exists():
                return Response({'Bad Request': f'User is not a chatroom participant!'}, status=status.HTTP_404_NOT_FOUND)
            chatroom.admins.add(admin)
        if request.method == 'DELETE':
            chatroom.admins.remove(admin)

        serializer = UserSerializer(chatroom.admins.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatroomParticipantListViewMixin(ChatroomParticipantListPermissionsMixin, UserMixin, ChatroomMixin):

    def get_queryset(self, queryset=None):
        return super().get_queryset(queryset)

    def get_participant_from_request(self, request):
        participant_id = request.data.get('id')
        try:
            return User.objects.get(pk=participant_id)
        except User.DoesNotExist:
            return None

    def list_participants(self, request):
        chatroom = self.get_chatroom_from_request(request)
        if isinstance(chatroom, Chatroom):
            serializer = UserSerializer(
                self.get_queryset(queryset=chatroom.participants.all()),
                many = True,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Bad Request': 'Object not found!'}, status=status.HTTP_404_NOT_FOUND)

    def perform_add_or_delete_participant(self, request):
        chatroom = self.get_chatroom_from_request(request)
        if not isinstance(chatroom, Chatroom):
            return Response({'Bad Request': f'Chatroom not found!'}, status=status.HTTP_404_NOT_FOUND)
        participant = self.get_participant_from_request(request)
        if not isinstance(participant, User):
            return Response({'Bad Request': f'Participant not found!'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            chatroom.participants.add(participant)
        if request.method == 'DELETE':
            chatroom.participants.remove(participant)

        serializer = UserSerializer(chatroom.participants.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
