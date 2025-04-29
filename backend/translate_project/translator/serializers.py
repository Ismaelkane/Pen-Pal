from rest_framework import serializers
from .models import Conversation, Message, CustomUser, groupConversation, GroupMessage

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('sender', 'receiver', 'text', 'translated_text', 'timestamp')

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)

    class Meta:
        model = Conversation
        fields = ('user1', 'user2', 'messages')



class GroupMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessage
        fields = '__all__'

class GroupConversationSerializer(serializers.ModelSerializer):
    messages = GroupMessageSerializer(many=True, read_only=True)

class Meta:
        model = groupConversation
        fields = ['group_name', 'user1', 'user2', 'user3', 'user4']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'language','language_text']  # Use lowercase fields

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)  # Create user with validated data
        return user