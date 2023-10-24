from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("Support/", views.room, name="support"),
    path('Conversations/', views.chats, name='allchats'),
    path('Chat/<str:chat_id>/Support/', views.room_support, name='room-support')
]