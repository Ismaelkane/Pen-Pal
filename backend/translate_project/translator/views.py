from django.shortcuts import get_object_or_404
from django.http import JsonResponse
#from django.contrib.auth.models import User

from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import os
from .models import Message, Conversation, UserConversation, groupConversation, GroupMessage
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt  # For testing
import json
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
#from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the homepage!")

User = get_user_model()
class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)  # Validates input data
            user = serializer.save()  # Save user and get instance

            return Response(
                {"user_id": user.id, "message": "Registration successful"},
                status=status.HTTP_201_CREATED
            )
        
        except ValidationError as e:  # Catch validation errors
            return Response(
                {"error": e.detail},  # Returns validation error details
                status=status.HTTP_400_BAD_REQUEST
            )

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        # Get the JSON data from the request body
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        print(f"Attempting to authenticate user: {username}")
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Successful login, return user id as JSON
            print(f"User authenticated successfully: {user.username}")
            return JsonResponse({'username': user.username,'user_id': user.id}, status=200)
        else:
            # Invalid login credentials
            print(f"Invalid credentials for user: {username}")
            return JsonResponse({'error': 'Invalid username or password.'}, status=400)
    return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)


def get_translate_client():
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    )
    return translate.Client(credentials=credentials)

@csrf_exempt
def change_language(request):
    if request.method == 'POST':
        # Parse JSON from request body
        data = json.loads(request.body)

        user_id = data.get('user_id')
        new_language = data.get('new_language')
        new_language_text = data.get('new_language_text')

        try:
            user = CustomUser.objects.get(id=user_id)
            user.language = new_language
            user.language_text = new_language_text
            user.save()

            return JsonResponse({
                "user": user.username,
                "new_language": user.language,
                "language_text": user.language_text
            })
        
        except CustomUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)

def find_user(request):
    currentUser = request.GET.get('user1')
    user2 = request.GET.get('user2')
    if not currentUser:
        return JsonResponse({"error": "user1 parameter is required"}, status=400)
    
    if not user2:
        return JsonResponse({"error": "user2 parameter is required"}, status=400)
    
    try:
        foundUser = CustomUser.objects.get(username=user2)
        currUser = CustomUser.objects.get(username= currentUser)
        
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

     # Get all conversations where the user is either user1 or user2
    conversations = (Conversation.objects.filter(user1=foundUser) &  Conversation.objects.filter(user2=currUser)) | (Conversation.objects.filter(user1=currUser) &  Conversation.objects.filter(user2=foundUser))
    convo_id = conversations.first().id if conversations.exists() else -1 
    

   
    return JsonResponse({"user2_name": foundUser.username,"user2_id": foundUser.id, "user2_language": foundUser.language,"user2_language_text": foundUser.language_text ,"convo_id":convo_id})


def get_user_info(request):
    currentUser = request.GET.get('user1')
    if not currentUser:
        return JsonResponse({"error": "user1 parameter is required"}, status=400)
    try:
        currUser = CustomUser.objects.get(id= currentUser)
    
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    
    return JsonResponse({"user_name": currUser.username, "user_language": currUser.language_text, "user_language_code": currUser.language })







def list_supported_languages(request):
     translate_client = get_translate_client()
     all_languages = translate_client.get_languages()
     languages_list = []
     for language in all_languages:
        print("{name} ({language})".format(**language))
        languages_list.append((language['name'], language['language'])) 


     return JsonResponse({'languages': languages_list})




#Create conversationGroup
@csrf_exempt
def createGroupConversation(request):
    if request.method == "POST":
        data = json.loads(request.body)
        group_name = data.get('group_name')
        user1 = User.objects.get(id=data.get('user1')) if data.get('user1') else None
        user2 = User.objects.get(id=data.get('user2')) if data.get('user2') else None
        user3 = User.objects.get(id=data.get('user3')) if data.get('user3') != -1 else None
        user4 = User.objects.get(id=data.get('user4')) if data.get('user4') != -1 else None
        conversation = groupConversation.objects.create(
                group_name=group_name,
                user1=user1,
                user2=user2,
                user3=user3,
                user4=user4
            )    
        return JsonResponse({
                "message": "Group conversation created successfully",
                "conversation_id": conversation.id,
                "conversation_name": conversation.group_name
            }, status=201)
    
    
    else:
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)





@csrf_exempt
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        sender_id = data.get('sender')
        receiver_id = data.get('receiver')
        text = data.get('text')
        target_language = data.get('lang')

        if not sender_id or not receiver_id or not text or not target_language:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        User = get_user_model()
        sender = get_object_or_404(User, id=sender_id)
        receiver = get_object_or_404(User, id=receiver_id)

        # Retrieve or create a conversation between the two users, checking both directions
        conversation = Conversation.objects.filter(
            (Q(user1=sender) & Q(user2=receiver)) | (Q(user1=receiver) & Q(user2=sender))
        ).first()

        # If no conversation exists, create a new one
        if not conversation:
            conversation = Conversation.objects.create(user1=sender, user2=receiver)

        # Use your existing Google Translation API client to translate the text
        translate_client = get_translate_client()
        translation = translate_client.translate(text, target_language=target_language)
        translated_text = translation.get('translatedText', '')

        # Create the new message with the translated text
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            text=text,
            translated_text=translated_text,
            language=target_language
        )
        conversation.messages.add(message)

        # Create or update the UserConversation entries for both users
        #UserConversation.objects.get_or_create(user=sender, conversation=conversation)
        #UserConversation.objects.get_or_create(user=receiver, conversation=conversation)

        return JsonResponse({
            'message_id': message.id,
            'sender_username': sender.username,
            'receiver_username': receiver.username,
            'original_text': text,
            'translated_text': translated_text,
            'language': message.language,
            'timestamp': message.timestamp
        })
    else:
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)




def get_messages(request):
    conversation_id = request.GET.get('conversation_id')

    if not conversation_id:
        return JsonResponse({"error": "conversation_id parameter is required"}, status=400)

    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return JsonResponse({"error": "Conversation not found"}, status=404)

    # Retrieve messages where either user in the conversation is involved
    messages = Message.objects.filter(
        sender__in=[conversation.user1, conversation.user2],
        receiver__in=[conversation.user1, conversation.user2]
    ).order_by('-timestamp')

    message_list = [
        {
            "id": msg.id,
            "sender": msg.sender.username,
            "receiver": msg.receiver.username,
            "text": msg.text,
            "translated_text": msg.translated_text,
            "language": msg.language,
            "timestamp": msg.timestamp
        }
        for msg in messages
    ]
    
    return JsonResponse({"messages": message_list})



def get_all_conversation_ids(request):
    conversation_ids = Conversation.objects.values_list('id', flat=True)
    return JsonResponse({"conversation_ids": list(conversation_ids)})

from django.db.models import Q

def get_conversations(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return JsonResponse({"error": "user_id parameter is required"}, status=400)

    try:
        # Use CustomUser model to get the user
        user = CustomUser.objects.get(id=user_id)
        print(user.username)
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # Use Q to filter conversations where user is either user1 or user2, without duplicates
    conversations = Conversation.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).distinct()

    conversation_list = [
        {
            "id": conv.id,
            "user1": user.username,
            "user2": conv.user2.username if conv.user1 == user else conv.user1.username,  # Set name based on user
            "name": conv.user2.username if conv.user1 == user else conv.user1.username,  # Set name based on user
            "user2_id": conv.user2.id if conv.user1 == user else conv.user1.id,  # Set name based on user
            "user2_lan": conv.user2.language if conv.user1 == user else conv.user1.language,  # Set name based on user
            "user2_language_text": conv.user2.language_text if conv.user1 == user else conv.user1.language_text,
            "user1_id": user.id
        }
        for conv in conversations
    ]

    return JsonResponse({"conversations": conversation_list})




def get_group_messages(request):
    conversation_id = request.GET.get('conversation_id')
    user_id = request.GET.get('user_id')

    if not conversation_id or not user_id:
        return JsonResponse({"error": "conversation_id and user_id are required"}, status=400)

    try:
        conversation = groupConversation.objects.get(id=conversation_id)
    except groupConversation.DoesNotExist:
        return JsonResponse({"error": "Conversation not found"}, status=404)

    try:
        current_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    participants = [u for u in [conversation.user1, conversation.user2, conversation.user3, conversation.user4] if u]

    if current_user not in participants:
        return JsonResponse({"error": "User is not part of this conversation"}, status=403)

    # Fetch all messages related to this group
    messages = conversation.messages.filter(
        Q(sender=current_user) |
        Q(receiver1=current_user) |
        Q(receiver2=current_user) |
        Q(receiver3=current_user)
    ).order_by('-timestamp')
    prevmsg_id=-1
    message_list = []
    for msg in messages:
        receiver_data = [
            (msg.receiver1, msg.translated_text1),
            (msg.receiver2, msg.translated_text2),
            (msg.receiver3, msg.translated_text3),
        ]
        receivers = [(r, t) for r, t in receiver_data if r is not None]

        # Handle if user is the sender
        if msg.sender == current_user and receivers:
                receiver, _ = receivers[0]
                message_list.append({
                    "id": msg.id,
                    "sender": msg.sender.username,
                    "receiver": receiver.username,
                    "text": msg.text,
                    "translated_text": ""
                })
               # break

        # Handle if user is one of the receivers
       
        for receiver, translated_text in receivers:
            if receiver == current_user:
                message_list.append({
                    "id": msg.id,
                    "sender": msg.sender.username,
                    "receiver": receiver.username,
                    "text": msg.text,
                    "translated_text": translated_text
                })
                break
            

    return JsonResponse({"messages": message_list})





@csrf_exempt
def send_group_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        group_id = data.get('group_id')
        sender_id = data.get('sender')
        text = data.get('text')

        if not sender_id or not text or not group_id:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            group_chat = groupConversation.objects.get(id=group_id)
            sender = CustomUser.objects.get(id=sender_id)
        except (groupConversation.DoesNotExist, CustomUser.DoesNotExist):
            return JsonResponse({"error": "Group or sender not found"}, status=404)

        # Collect receivers (excluding sender)
        participants = [group_chat.user1, group_chat.user2, group_chat.user3, group_chat.user4]
        receivers = [user for user in participants if user and user.id != sender.id][:3]  # max 3 receivers

        translate_client = get_translate_client()

        # Create field-specific receiver data
        receiver_fields = [None, None, None]
        translated_texts = ["", "", ""]
        languages = ["", "", ""]

        for i, receiver in enumerate(receivers):
            translation = translate_client.translate(text, target_language=receiver.language)
            receiver_fields[i] = receiver
            translated_texts[i] = translation.get('translatedText', '')
            languages[i] = receiver.language

        # Create the GroupMessage object
        message = GroupMessage.objects.create(
            sender=sender,
            text= text,
            receiver1=receiver_fields[0],
            receiver2=receiver_fields[1],
            receiver3=receiver_fields[2],
            translated_text1=translated_texts[0],
            translated_text2=translated_texts[1],
            translated_text3=translated_texts[2],
            language1=languages[0],
            language2=languages[1],
            language3=languages[2],
        )
        # Add message to group conversation
        group_chat.messages.add(message)
        print(f"Message {message.id} added to group {group_chat.id}")

        return JsonResponse({
            "message": "Message sent successfully",
            "original_text": text,
            "receivers": [
                {
                    "username": r.username,
                    "language": l,
                    "translated_text": t
                } for r, l, t in zip(receiver_fields, languages, translated_texts) if r
            ]
        })

    else:
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)











def get_group_conversations(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return JsonResponse({"error": "user_id parameter is required"}, status=400)

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    conversations = groupConversation.objects.filter(
        Q(user1=user) | Q(user2=user) | Q(user3=user) | Q(user4=user)
    ).distinct()

    conversation_list = []

    for conv in conversations:
        # Build a list of other participants, excluding the current user
        other_users = []
        for u in [conv.user1, conv.user2, conv.user3, conv.user4]:
            if u and u != user:
                other_users.append(u)

        # Assign participants for consistency
        convo_data = {
            "id": conv.id,
            "group_name": conv.group_name,
            "user1": user.username,
            "user1_id": user.id,
            "user1_lan": user.language,
        }

        # Fill in user2, user3, user4 if available
        for i in range(3):  # Only room for user2-4
            if i < len(other_users):
                convo_data[f"user{i+2}"] = other_users[i].username
                convo_data[f"user{i+2}_id"] = other_users[i].id
                convo_data[f"user{i+2}_lan"] = other_users[i].language
            #else:
             #   convo_data[f"user{i+2}"] = None
              #  convo_data[f"user{i+2}_id"] = None
               # convo_data[f"user{i+2}_lan"] = None

        conversation_list.append(convo_data)

    return JsonResponse({"conversations": conversation_list})



CustomUser = get_user_model()

def get_user(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return JsonResponse({"error": "user_id parameter is required"}, status=400)

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({"username": user.username})