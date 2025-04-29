from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Custom User model
class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    first_name=models.CharField(max_length=150)
    last_name= models.CharField(max_length=150)
    email = models.EmailField(unique=True)  # Enforce unique email
    language = models.CharField(
        max_length=10
    )
    language_text = models.CharField(max_length=150, default="English")


class GroupMessage(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_group_messages'
    )
    
    receiver1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_group_messages_1'
    )
    receiver2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_group_messages_2',
        null=True,
        blank=True
    )
    receiver3 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_group_messages_3',
        null=True,
        blank=True
    )
    
    text = models.TextField()
    
    translated_text1 = models.TextField()
    translated_text2 = models.TextField()
    translated_text3 = models.TextField()
    
    language1 = models.CharField(max_length=10)
    language2 = models.CharField(max_length=10)
    language3 = models.CharField(max_length=10)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {[self.receiver1, self.receiver2, self.receiver3]} at {self.timestamp}"


#group conversation model
class groupConversation(models.Model):
    group_name = models.CharField(max_length=100, blank=True, null=True)
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_conversations_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_conversations_user2')
    user3 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_conversations_user3', null=True, blank=True)
    user4 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_conversations_user4', null=True, blank=True)
    messages = models.ManyToManyField('GroupMessage')

    class Meta:
        constraints = []

    def __str__(self):
        return f"{self.group_name} : {self.id}"


# Message model
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    translated_text = models.TextField()
    language = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

# Conversation model between two users
class Conversation(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations_user2')
    messages = models.ManyToManyField(Message)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_conversation')
        ]

    def __str__(self):
        return f"Conversation between {self.user1} and {self.user2}"

# Join model linking a user to a conversation
class UserConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_conversations')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='user_conversations')
    # You can also add fields like last_read or notifications here if desired

    class Meta:
        unique_together = ('user', 'conversation')

    def __str__(self):
        return f"{self.user.username}'s view of {self.conversation}"
