from django.urls import path
from . import views
from .views import RegisterView

urlpatterns = [
    path('send_message/', views.send_message, name='send_message'),  # POST endpoint for sending messages
    path('get_messages/', views.get_messages, name='get_messages'),  # GET endpoint for getting messages
    path('get_conversations/', views.get_conversations, name='get_conversations'),
    path('get_user/', views.get_user, name='get_user'),
    path('register/', RegisterView.as_view(), name='register'),
    path('supported_languages/',views.list_supported_languages, name='supported_languages'),
    path('find_user/',views.find_user, name='find_user'),
    path('user_login/',views.user_login, name='user_login'),
    path('allconv/',views.get_all_conversation_ids, name='allconv'),
    path('create_group_convo/',views.createGroupConversation, name='create_group_convo'),
    path('get_group_conversations/',views.get_group_conversations, name='get_group_conversations'),
    path('send_group_message/',views.send_group_message, name='send_group_message'),
    path('change_language/',views.change_language, name='change_language'),
    path('get_user_info/',views.get_user_info, name='get_user_info'),
    path('get_group_messages/',views.get_group_messages, name='get_group_messages'),
    path('', views.home, name='home'),

]
