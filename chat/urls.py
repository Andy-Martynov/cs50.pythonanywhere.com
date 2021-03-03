from django.urls import path

from . import views, api

app_name = 'chat'
urlpatterns = [
    path("", views.index, name="index"),

    path("message_list/<int:id1>/<int:id2>", api.message_list, name="message_list"),
    path("message", api.message, name="message"),

    path("group_message_list/<int:id>", api.group_message_list, name="group_message_list"),
    path("group_message", api.group_message, name="group_message"),

    path("clear_sender_unread/<int:user_id>/<int:sender_id>", api.clear_sender_unread, name="clear_sender_unread"),
    path("clear_group_unread/<int:user_id>/<int:group_id>", api.clear_group_unread, name="clear_group_unread"),
    path("unread_list", api.unread_list, name="unread_list"),

    path("typing/<int:user_id>/<str:mode>/<int:id>", api.typing, name="typing"),
]