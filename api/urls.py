from django.urls import path

from api import views


app_name = 'api'
urlpatterns = [
    path('users', views.UserListView.as_view(), name='users'),
    path('users/<int:pk>', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/friends', views.UserFriendListView.as_view(), name='user-friends'),

    path('messages', views.MessageListView.as_view(), name='messages'),
    path('messages/<int:pk>', views.MessageDetailView.as_view(), name='message-detail'),

    path('chatrooms', views.ChatroomListView.as_view(), name='chatrooms'),
    path('chatrooms/<int:pk>', views.ChatroomDetailView.as_view(), name='chatroom-detail'),
    path('chatrooms/<int:pk>/messages', views.ChatroomMessageListView.as_view(), name='chatroom-messages'),
    path('chatrooms/<int:pk>/admins', views.ChatroomAdminListView.as_view(), name='chatroom-admins'),
    path('chatrooms/<int:pk>/participants', views.ChatroomParticipantListView.as_view(), name='chatroom-participants'),
]
