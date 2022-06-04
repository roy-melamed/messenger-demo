from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from .models import Messages, Inbox, Outbox
from .serializers import MessagesSerializer, RegisterSerializer, InboxSerializer, OutboxSerializer
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt


class MessagesApiView(APIView):

    # 1. write message
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        data = {
            'content': request.data.get('content'),
            'subject': request.data.get('subject'),
            'receiver': request.data.get('receiver'),
            'sender': request.user.id,
        }
        serializer = MessagesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            inbox_data = {
                'receiver': serializer.data['receiver'],
                'message': serializer.data['id']
            }
            outbox_data = {
                'sender': serializer.data['sender'],
                'message': serializer.data['id']
            }
            inbox_serializer = InboxSerializer(data=inbox_data)
            outbox_serializer = OutboxSerializer(data=outbox_data)
            if inbox_serializer.is_valid() and outbox_serializer.is_valid():
                inbox_serializer.save()
                outbox_serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 2. get all messages for a specific user
    @csrf_exempt
    def get(self, request, *args, **kwargs):
        messages = Messages.objects.all()
        serializer = MessagesSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# add user for authentication
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


# should be modified for admin usage only
class MessagesByUserView(APIView):

    # 1. get all messages for a specific user
    @csrf_exempt
    def get(self, request, *args, **kwargs):
        return Response("HELLO")
        # messages = Messages.objects.filter(Q(receiver=kwargs['id']) | Q(sender=kwargs['id']))
        # serializer = MessagesSerializer(messages, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)


class InboxView(APIView):
    @csrf_exempt
    def get(self, request, *args, **kwargs):
        try:
            # get all the unread messages from the user's inbox
            if request.query_params['unread_only'] == 'true':
                messages_ids = Inbox.objects.filter(read=0, receiver=request.user.id).values_list('message')
                messages = Messages.objects.filter(id__in=messages_ids)
                if not messages:
                    return Response("You are all caught up :)", status=status.HTTP_200_OK)
                serializer = MessagesSerializer(messages, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response("unread_only flag can either be passed with true or not passed at all",
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            try:
                # get a specific message by id from user's inbox
                # and update read flag to 1(message that already been read)
                messages_ids = Inbox.objects.filter(receiver=request.user.id,
                                                    message=int(request.query_params['message_id'])) \
                    .values_list('message')
                if not messages_ids:
                    return Response("Message id doesn't exist", status=status.HTTP_400_BAD_REQUEST)
                Inbox.objects.filter(receiver=request.user.id,
                                     message=int(request.query_params['message_id'])).update(read=1)
                messages = Messages.objects.filter(id__in=messages_ids)
                serializer = MessagesSerializer(messages, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                messages_ids = Inbox.objects.filter(receiver=request.user.id).values_list('message')
                messages = Messages.objects.filter(id__in=messages_ids)
                serializer = MessagesSerializer(messages, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

    # deleting message from inbox only and not from general messages table
    @csrf_exempt
    def delete(self, request, *args, **kwargs):
        messages_ids = Inbox.objects.filter(receiver=request.user.id,
                                            message=int(request.query_params['message_id'])).values_list('message')
        if not messages_ids:
            return Response("Message id doesn't exist", status=status.HTTP_400_BAD_REQUEST)
        Inbox.objects.filter(receiver=request.user.id, message=int(request.query_params['message_id'])).delete()
        return Response("Message deleted from inbox", status=status.HTTP_200_OK)


class OutboxView(APIView):

    # 1. get all messages from the user's outbox
    @csrf_exempt
    def get(self, request, *args, **kwargs):
        try:
            # get a specific message by id from user's outbox
            messages_ids = Outbox.objects.filter(sender=request.user.id,
                                                 message=int(request.query_params['message_id'])).values_list('message')
            if not messages_ids:
                return Response("Message id doesn't exist", status=status.HTTP_400_BAD_REQUEST)
            messages = Messages.objects.filter(id__in=messages_ids)
            serializer = MessagesSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            messages_ids = Outbox.objects.filter(sender=request.user.id).values_list('message')
            messages = Messages.objects.filter(id__in=messages_ids)
            if not messages:
                return Response("Outbox is empty", status=status.HTTP_200_OK)
            serializer = MessagesSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # deleting message from outbox only and not from general messages table
    @csrf_exempt
    def delete(self, request, *args, **kwargs):
        messages_ids = Outbox.objects.filter(sender=request.user.id,
                                             message=int(request.query_params['message_id'])).values_list('message')
        if not messages_ids:
            return Response("Message id doesn't exist", status=status.HTTP_400_BAD_REQUEST)
        Outbox.objects.filter(sender=request.user.id, message=int(request.query_params['message_id'])).delete()
        return Response("Message deleted from inbox", status=status.HTTP_200_OK)
