from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required

import json
import pusher
from pusher_push_notifications import PushNotifications

from account.models import User, Group, Membership
from .models import Message, GroupMessage, Unread


@login_required
def message_list(request, id1, id2):
    user1 = User.objects.filter(id=id1).first()
    user2 = User.objects.filter(id=id2).first()
    if user1 and user2:
        messages1 = Message.objects.filter(sender=user1, reciever=user2)
        messages2 = Message.objects.filter(sender=user2, reciever=user1)
        messages = messages1.union(messages2)
        info = []
        for message in messages:
            info.append(message.serialize())
        return JsonResponse(info, status=200, safe=False)
    return JsonResponse({'error': f'user {id1} or {id2} not found'}, status=404)

@login_required
def group_message_list(request, id):
    group = Group.objects.filter(id=id).first()
    if group:
        messages = GroupMessage.objects.filter(reciever=group).reverse()
        info = []
        for message in messages:
            info.append(message.serialize())
        return JsonResponse(info, status=200, safe=False)
    return JsonResponse({'error': f'group {id} not found'}, status=404)

@login_required
def unread_list(request):
    unreads = Unread.objects.filter(user=request.user)
    info = []
    for unread in unreads:
        info.append(unread.serialize())
    return JsonResponse(info, status=200, safe=False)

@csrf_exempt
@login_required
def message(request):
    pusher_client = pusher.Pusher(
      app_id='1152832',
      key='bbe70803665a7a964619',
      secret='541db5cfad7af600f737',
      cluster='eu',
      ssl=True
    )
    beams_client = PushNotifications(
        instance_id='4db9511e-c5da-4d6f-8f58-9fbee669a07f',
        secret_key='1084B2BACEE2B3988B64C932B6842735CEB36BC1DAFB7A493FA130E604169778',
    )

    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("to") is not None:
            to = data["to"]
            reciever = User.objects.filter(id=to).first()
            if reciever :
                if data.get("text") is not None:
                    text = data["text"]
                    msg = Message.objects.create(sender=request.user, reciever=reciever, text=text)
                    data = {}
                    data['message'] = msg.serialize()
                    pusher_client.trigger('private-my-channel', 'message-sent', data)
                    data = {}
                    data['user'] = reciever.id
                    pusher_client.trigger('private-my-channel', 'sent-to-user', data)

                    user_ids = []
                    user_ids.append(str(reciever.id))
                    response = beams_client.publish_to_users(
                        user_ids=user_ids,
                        publish_body={
                        'web': {
                          'notification': {
                            'title': 'Message',
                            'body': f'{reciever.username}, you have a message from {request.user.username}',
                            'deep_link': 'https://cs50.pythonanywhere.com',
                          },
                        },
                      },
                    )

                    unreads = Unread.objects.filter(user=reciever, sender=request.user)
                    if not unreads:
                        Unread.objects.create(user=reciever, sender=request.user)
                    return JsonResponse({'status': '200', 'response': response})
                return HttpResponse(status=404)
            return HttpResponse(status=414)
        return HttpResponse(status=424)
    else:
        return HttpResponse(status=400)

@csrf_exempt
@login_required
def group_message(request):
    pusher_client = pusher.Pusher(
      app_id='1152832',
      key='bbe70803665a7a964619',
      secret='541db5cfad7af600f737',
      cluster='eu',
      ssl=True
    )
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("to") is not None:
            to = data["to"]
            reciever = Group.objects.filter(id=to).first()
            if reciever :
                if data.get("text") is not None:
                    text = data["text"]
                    msg = GroupMessage.objects.create(sender=request.user, reciever=reciever, text=text)
                    data = {}
                    data['message'] = msg.serialize()
                    pusher_client.trigger('private-my-channel', 'group-message-sent', data)

                    memberships = Membership.objects.filter(group=reciever)
                    for membership in memberships:
                        data = {}
                        data['group'] = membership.group.serialize()
                        data['mode'] = 'group'
                        data['user'] = membership.user.id
                        pusher_client.trigger('private-my-channel', 'sent-to-user', data)
                        unreads = Unread.objects.filter(group=reciever, user=membership.user)
                        if not unreads:
                            Unread.objects.create(group=reciever, user=membership.user)
                    return HttpResponse(status=200)
                return HttpResponse(status=404)
            return HttpResponse(status=414)
        return HttpResponse(status=424)
    else:
        return HttpResponse(status=400)

@login_required
def typing(request, user_id, mode, id):
    pusher_client = pusher.Pusher(
      app_id='1152832',
      key='bbe70803665a7a964619',
      secret='541db5cfad7af600f737',
      cluster='eu',
      ssl=True
    )
    user = User.objects.filter(id=user_id).first()
    if user:
        data = {}
        data['from'] = user.serialize()
        data['mode'] = mode
        data['to'] = id
        pusher_client.trigger('private-my-channel', 'typing', data)
        return HttpResponse(status=200)
    return HttpResponse(status=404)

@csrf_exempt
@login_required
def clear_sender_unread(request, user_id, sender_id):
    user = User.objects.filter(id=user_id).first()
    sender = User.objects.filter(id=sender_id).first()
    if user and sender:
        unread = Unread.objects.filter(sender=sender, user=user)
        if unread:
            unread.delete()
            return HttpResponse(200)
        return HttpResponse(f'unreads not found', status=200)
    return HttpResponse(f'user {user_id} or {sender_id} not found', status=404)

@login_required
def clear_group_unread(request, user_id, group_id):
    user = User.objects.filter(id=user_id).first()
    group = Group.objects.filter(id=group_id).first()
    if user and group:
        unread = Unread.objects.filter(group=group, user=user)
        if unread:
            unread.delete()
            return HttpResponse(200)
        return HttpResponse(f'unreads not found', status=200)
    return HttpResponse(f'user {user_id} or group {group_id} not found', status=404)



