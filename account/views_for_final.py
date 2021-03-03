from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.db.models import Count
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

import random
from PIL import Image

from .models import User, Group, Membership
from .forms import UserForm, UserImageForm, GroupForm

def index(request) :
    return render(request, "hub/index.html")

@login_required
def get_all_logged_in_users():
    # Query all non-expired sessions
    # use timezone.now() instead of datetime.now() in latest versions of Django
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return User.objects.filter(id__in=uid_list)

class UserList(LoginRequiredMixin, ListView) :
    model = User
    template_name = 'account/user_list.html'

    def get_queryset(self):
        users = User.objects.order_by('username')
        list = []
        for user in users :
            item = {}
            item['user'] = user
            memberships = Membership.objects.filter(user=user)
            item['memberships'] = memberships
            list.append(item)
        return list

@login_required
def resize_260x260(request, id) :
    user = User.objects.filter(id=id).first()
    if user :
        f = user.fullname()
        try :
            image = Image.open(f)
            if image :
                image.thumbnail((260,260))
                image.save(f)
        except :
            messages.info(request, 'resize failed', extra_tags='alert-danger')
        try :
            user.save()
        except :
            messages.info(request, 'WTF?', extra_tags='alert-danger')
    return redirect(reverse('meeting:index'))

@login_required
def user_image_update(request, id=0) :

    if id == 0 :
        user = request.user
    else :
        user = User.objects.filter(id=id).first()

    if request.method == 'POST':
        form = UserImageForm(request.POST, request.FILES)
        if form.is_valid():
            user.image = form.cleaned_data['image']
            try :
                user.save()
            except :
                messages.info(request, 'WTF?', extra_tags='alert-danger')
            return redirect(reverse('account:resize_260x260', args=[user.id]))
    else:
        form = UserImageForm(initial={
            'username': user.username,
            })
    return render(request, 'account/user_image_form.html', {'form': form, 'person': user})

@login_required
def user_update(request) :
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']
            try :
                request.user.save()
            except :
                messages.info(request, 'WTF?', extra_tags='alert-danger')
            # redirect to a new URL:
            return render(request, "meeting/index.html")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserForm(initial={
            'username': request.user.username,
            'email': request.user.email,
            })
    return render(request, 'account/user_form.html', {'form': form})

# _________________________________________________ GROUP ______________________

class GroupList(LoginRequiredMixin, ListView) :
    model = Group

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        groups = Group.objects.all().annotate(Count('members'));

        group_list = []

        for group in groups :
            item = {}
            item['group'] = group
            memberships = Membership.objects.filter(group=group)
            count = memberships.count()
            item['count'] = count
            members = []
            for membership in memberships :
                members.append(membership.user)
            item['members'] = members
            group_list.append(item)
        context['group_list'] = group_list
        return context

class GroupDetail(LoginRequiredMixin, DetailView) :
    model = Group

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        if 'pk' in self.kwargs :
            pk = self.kwargs['pk']
            group = Group.objects.filter(id=pk).first();

            users=User.objects.order_by('username')

            memberships = Membership.objects.filter(group=group)
            count = memberships.count()
            members = []
            for membership in memberships :
                members.append(membership.user)
                users = users.exclude(id=membership.user.id)
            users_count = users.count()
            context['count'] = count
            context['users_count'] = users_count
            context['members'] = members
            context['group'] = group
            context['users_not_in_group'] = users
        return context


class GroupCreate(LoginRequiredMixin, CreateView) :
    model = Group
    form_class = GroupForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        self.success_url = reverse('account:group_list')
        return super().form_valid(form)


class GroupUpdate(LoginRequiredMixin, UpdateView) :
    model = Group
    form_class = GroupForm
    template_name = 'account/group_update_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        if 'pk' in self.kwargs :
            pk = self.kwargs['pk']
            group = Group.objects.filter(id=pk).first();

            users=User.objects.order_by('username')

            memberships = Membership.objects.filter(group=group)
            count = memberships.count()
            members = []
            for membership in memberships :
                members.append(membership.user)
                # users = users.exclude(id=membership.user.id)
            users_count = users.count()
            context['count'] = count
            context['users_count'] = users_count
            context['members'] = members
            context['group'] = group
            context['users_not_in_group'] = users
        return context

    def form_valid(self, form):
        self.success_url = reverse('account:group_list')
        return super().form_valid(form)


@login_required
def group_delete(request, pk) :
    group = Group.objects.filter(id=pk).first()
    if group :
        if (group.creator == request.user) or request.user.is_superuser :
            group.delete()
        else :
            messages.info(request, "You are not allowed to delete someone else'e group", extra_tags='alert-danger')
    return redirect(reverse('hub:index'))

# _________________________________________________ LOGIN REGISTER LOGOUT ______

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if 'who_logged_in' in request.session :
                url = request.session['who_logged_in']
            else :
                url = reverse("meeting:index")
            request.session['who_logged_in'] = ''
            # return HttpResponseRedirect(url)
            return HttpResponseRedirect(reverse("meeting:index"))
        else:
            return render(request, "account/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        request.session['who_logged_in'] = request.META.get('HTTP_REFERER')
        return render(request, "account/login.html")


def logout_view(request):
    logout(request)
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(reverse("meeting:index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "account/register.html", {
                "message": "Passwords must match."
            })

        # somebody = User.objects.filter(email=email).first()
        # if somebody :
        #     return render(request, "account/register.html", {
        #         "message": f'{email} is already in use'
        #     })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "account/register.html", {
                "message": "Username already taken."
            })
        login(request, user)

        user.is_active = False
        user.save()

        # manager = Manager.objects.create(user=user)
        token = random.randint(0, 1000000)*1000+user.id
        user.token = token
        user.save()

        url = 'http://cs50.pythonanywhere.com/account/confirm/'+str(token)

        html = '''\
<div>
<p>Подтверждение адреса email</p>
<br>
<p><a href="''' + url + '''"><button style="color: #ffffff; background-color: #000066; align: center;">OK</button></a></p>
<br>
<p>Спасибо!</p>
</div>'''

        sent = send_mail(
        f'Регистрация {username} {email}',
        '',
        'andymartynovmail@gmail.com',
        [email],
        fail_silently=False,
        html_message = html,
        )

        url = request.session['who_registred']
        request.session['who_registred'] = ''

        logout(request)
        if sent == 0 :
            messages.info(request, f'failed send confirmation email to {email}', extra_tags='alert-danger')
        else :
            messages.info(request, f'Confirmation email has been sent to {email}', extra_tags='alert-success')

        return HttpResponseRedirect(url)
        # return HttpResponseRedirect(reverse("meeting:index"))
    else:
        request.session['who_registred'] = request.META.get('HTTP_REFERER')
        return render(request, "account/register.html")

def confirm_email(request, token) :
    id = token % 1000
    user = User.objects.filter(id=id).first()
    if user :
        if user.token == token :
            user.is_active = True
            user.save()
            send_mail(
            f'{user.username} {user.email} registred',
            '',
            'andymartynovmail@gmail.com',
            ['andymartynovmail@gmail.com'],
            fail_silently=False,
            )
            return HttpResponse('Email confirmed, thanks!')
        return HttpResponse('400 invalid token')
    return HttpResponse(f'401, user id {id} not found {user}')



