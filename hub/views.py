from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.db.models import Count
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from network.models import Post, Like
from network.forms import PostForm
from account.models import User, Group, Membership
from todo.models import Task, Share
from todo.views import get_unread_task_shared_to_me

import pusher
from pusher_push_notifications import PushNotifications

beams_client = PushNotifications(
    instance_id='4db9511e-c5da-4d6f-8f58-9fbee669a07f',
    secret_key='1084B2BACEE2B3988B64C932B6842735CEB36BC1DAFB7A493FA130E604169778',
)


@csrf_exempt
def pusher_auth(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    pusher_client = pusher.Pusher(
      app_id='1152832',
      key='bbe70803665a7a964619',
      secret='541db5cfad7af600f737',
      cluster='eu',
      ssl=True
    )
    image_url = None
    if request.user.image:
        if request.user.image.url:
            image_url = request.user.image.url
    payload = pusher_client.authenticate(
        channel=request.POST['channel_name'],
        socket_id=request.POST['socket_id'],
        custom_data={
            'user_id': request.user.id,
            'user_info': {  # We can put whatever we want here
                'username': request.user.username,
                'image': image_url,
                # 'my_groups': my_groups,
                # 'groups_im_in': groups_im_in,
            }
        })
    return JsonResponse(payload)

@csrf_exempt
def pusher_beams_auth(request, user_id=None):
    # if not request.user.is_authenticated:
    #     return HttpResponse('User is not authenticated', 403)

    # if user_id != request.user.id:
    #     return HttpResponse('Inconsistent request', 401)

    beams_token = beams_client.generate_token(str(user_id))
    return JsonResponse(beams_token) # {'token': beams_token})


@login_required
def hello(request, text):
    pusher_client = pusher.Pusher(
      app_id='1152832',
      key='bbe70803665a7a964619',
      secret='541db5cfad7af600f737',
      cluster='eu',
      ssl=True
    )
    data = {}
    data['username'] = request.user.username
    data['user_id'] = request.user.id
    data['message'] = f'{request.user.username}: {text}'
    pusher_client.trigger('my-channel', 'message-to-all', data)
    return JsonResponse({'message': f'notifiation from {request.user.username} sent'})

@login_required
def beam_hello(request, text):
    response = beams_client.publish_to_interests(
      interests=['hello'],
      publish_body={
        'web': {
          'notification': {
            'title': f'From {request.user.username}',
            'body': text,
            'deep_link': 'https://cs50.pythonanywhere.com',
          },
        },
      },
    )
    return JsonResponse({'message': f'notifiation from {request.user.username} sent'})

@login_required
def beam_user_message(request, id):
    beams_client = PushNotifications(
        instance_id='4db9511e-c5da-4d6f-8f58-9fbee669a07f',
        secret_key='1084B2BACEE2B3988B64C932B6842735CEB36BC1DAFB7A493FA130E604169778',
    )
    user=User.objects.filter(id=id).first()
    if user:
        user_ids = []
        user_ids.append(str(id))
        response = beams_client.publish_to_users(
            user_ids=user_ids,
            publish_body={
            'web': {
              'notification': {
                'title': 'Message',
                'body': f'{user.username}, you have a message from {request.user.username}',
                'deep_link': 'https://cs50.pythonanywhere.com',
              },
            },
          },
        )
    return JsonResponse({'message': f'message from {request.user.username} sent to {user.username}, {response}'})


#_______________________________________________________________________________


def index(request):
    return redirect(reverse("hub:post_create"))


class PostCreate(CreateView) :
    model = Post
    form_class = PostForm
    template_name = "hub/index.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(comment=True).order_by('created').reverse().annotate(Count('like_me'))
        posts = posts.annotate(label=Count('like_me'))
        if self.request.user.is_authenticated :
            likes = Like.objects.filter(who=self.request.user)
            i_like = []
            for like in likes:
                i_like.append(like.post)
            context['i_like'] = i_like

        paginator = Paginator(posts, 10) # Show 10 per page.
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['count'] = posts.count()

        context['anchor'] = '#'
        context['kwargs'] = self.kwargs
        if 'anchor' in self.kwargs :
            context['anchor'] = self.kwargs['anchor']

        # Get new unrecieved tasks shared to me
        unrecieved_tasks, unrecieved_tasks_shares = get_unread_task_shared_to_me(self.request)
        context['unrecieved_tasks'] = unrecieved_tasks
        context['unrecieved_tasks_shares'] = unrecieved_tasks_shares
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.comment = True
        self.success_url = reverse("hub:post_create", kwargs={'anchor':'comments'})
        return super().form_valid(form)

class PostUpdate(UpdateView) :
    model = Post
    form_class = PostForm

@login_required
def post_delete(request, id=None):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if id:
                Post.objects.filter(id=id).delete()
    return redirect(reverse("hub:post_create"))



