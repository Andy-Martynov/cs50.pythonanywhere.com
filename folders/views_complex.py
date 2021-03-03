from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

import json

from account.models import User, Group, Membership
from .models import Folder, FolderShare
from .forms import FolderForm

@login_required
def index(request):
    return redirect(reverse('folders:folder_list'))

def folder_tree(user=None, parent=None, folder=None, tag=None):
    tree = []
    if folder:
        tree.append(folder)
        childs = folder_tree(parent=folder)
        tree.extend(childs)
        return tree
    if not parent :
        root = Folder.objects.filter(level=0, user=user, prev=None).first()
    else:
        root = Folder.objects.filter(parent=parent, prev=None).first()
    if tag:
        if root:
            tags = root.tag
            tag_list = tags.split()
            if not tag in tag_list:
                root = None
    while root:
        tree.append(root)
        childs = folder_tree(user, root)
        tree.extend(childs)
        root = root.next
    return tree

@csrf_exempt
@login_required
def add_share(request):
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("folder_id") is not None:
            folder_id = data["folder_id"]
            folder = Folder.objects.filter(id=folder_id).first()
            if folder :
                if data.get("user_id") is not None:
                    user_id = data["user_id"]
                    user = User.objects.filter(id=user_id).first()
                    if user :
                        if user != folder.user:
                            share = FolderShare.objects.filter(folder=folder, who=user).first()
                            if not share:
                                FolderShare.objects.create(folder=folder, who=user)
                                return HttpResponse(status=200)
                            return HttpResponse(status=201)
                        return HttpResponse(status=202)
                    return HttpResponse(status=404)
                return HttpResponse(status=400)
            return HttpResponse(status=414)
        return HttpResponse(status=410)
    else:
        return HttpResponse(status=401)

@csrf_exempt
@login_required
def remove_share(request):
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("folder_id") is not None:
            folder_id = data["folder_id"]
            folder = Folder.objects.filter(id=folder_id).first()
            if folder :
                if data.get("user_id") is not None:
                    user_id = data["user_id"]
                    user = User.objects.filter(id=user_id).first()
                    if user :
                        if user != folder.user:
                            share = FolderShare.objects.filter(folder=folder, who=user).first()
                            if share:
                                share.delete()
                                return HttpResponse(status=200)
                            return HttpResponse(status=201)
                        return HttpResponse(status=202)
                    return HttpResponse(status=404)
                return HttpResponse(status=400)
            return HttpResponse(status=414)
        return HttpResponse(status=410)
    else:
        return HttpResponse(status=401)

class FolderUpdate(LoginRequiredMixin, UpdateView) :
    model = Folder
    form_class = FolderForm
    success_url = reverse_lazy('folders:folder_list')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['folder_tree'] = folder_tree(user=self.request.user, parent=self.object)
        context['update'] = True
        return context

    def form_valid(self, form):
        return super().form_valid(form)


def folder_delete(request, pk=None):
    if not pk:
        messages.info(request, "Delete, No ID", extra_tags='alert-warning')
    folder = Folder.objects.filter(id=pk).first()
    if not folder:
        messages.info(request, f"Delete, No {pk} folder", extra_tags='alert-warning')
        return redirect(reverse('folders:folder_list'))
    prev = folder.prev
    next = folder.next
    if prev:
        prev.next = next
        if next:
            next.prev = prev
        prev.save()
    if next:
        next.prev = prev
        if prev:
            prev.next = next
        next.save()
    folder.delete()
    return redirect(reverse('folders:folder_list'))

def folder_share(request, pk=None):
    if not pk:
        messages.info(request, "Delete, No ID", extra_tags='alert-warning')
    folder = Folder.objects.filter(id=pk).first()
    if not folder:
        messages.info(request, f"Share, No {pk} folder", extra_tags='alert-warning')
        return redirect(reverse('folders:folder_list'))
    groups = Group.objects.all().annotate(Count('members'));
    groups = groups.filter(creator=request.user)
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
    shared = []
    shares = FolderShare.objects.filter(folder=folder)
    for share in shares:
        shared.append(share.who)
    return render(request, "folders/folder_share.html", {'folder': folder, 'group_list': group_list, 'shared': shared})


class FolderCreate(LoginRequiredMixin, CreateView) :
    model = Folder
    form_class = FolderForm
    success_url = reverse_lazy('folders:folder_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.save()

        if 'parent_id' in self.kwargs :
            parent_id = self.kwargs['parent_id']
            parent = Folder.objects.filter(id=parent_id).first()
            form.instance.parent = parent
            form.instance.user = parent.user
            form.instance.level = parent.level + 1

            prev = Folder.objects.filter(parent=parent, next=None).first()
            if prev:
                prev.next = form.instance
                prev.save()
            form.instance.prev = prev
        elif 'link_id' in self.kwargs :
            link_id = self.kwargs['link_id']
            mode = self.kwargs['mode']
            link = Folder.objects.filter(id=link_id).first()
            parent = link.parent
            form.instance.user = link.user
            form.instance.parent = parent
            if parent:
                form.instance.level = parent.level + 1

            if mode == 'after':
                form.instance.prev = link
                form.instance.next = link.next
                if link.next:
                    link.next.prev = form.instance
                    link.next.save()
                link.next = form.instance
                link.save()
            else:
                form.instance.prev = link.prev
                form.instance.next = link
                if link.prev:
                    link.prev.next = form.instance
                    link.prev.save()
                link.prev = form.instance
                link.save()
        else: # New level 0 folder
            form.instance.user = self.request.user
            prev = Folder.objects.filter(level=0, next=None, user=self.request.user).first()
            if prev:
                if prev != form.instance:
                    prev.next = form.instance
                    prev.save()
            if prev != form.instance:
                form.instance.prev = prev
        return super().form_valid(form)


class FolderList(LoginRequiredMixin, ListView) :
    model = Folder

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        if 'tag' in self.kwargs :
            tag = self.kwargs['tag']
            my_folders = folder_tree(user=self.request.user, tag=tag)
        else:
            my_folders = folder_tree(user=self.request.user)
        context['folder_tree'] = my_folders

        shared = []
        shared_to_me = FolderShare.objects.filter(who=self.request.user)
        for share in shared_to_me:
            shared.append(folder_tree(folder=share.folder))
        context['shared'] = shared

        i_share = FolderShare.objects.filter(folder__in=my_folders)
        context['i_share'] = i_share

        context['groups'] = Group.objects.filter(creator=self.request.user)
        return context

class FolderDetail(LoginRequiredMixin, DetailView) :
    model = Folder

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['folder_tree'] = folder_tree(user=self.request.user, parent=self.object)
        return context
