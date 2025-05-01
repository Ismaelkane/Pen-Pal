from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/conversations/(?P<user_id>\d+)/$", consumers.ConversationConsumer.as_asgi()),
]
