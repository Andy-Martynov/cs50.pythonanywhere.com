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
    return redirect(reverse('folders:folder_tree', kwargs={'user_id': request.user.id}))

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
        return context

    def form_valid(self, form):
        self.success_url = reverse_lazy('folders:folder_detail', kwargs={'pk': form.instance.id})
        return super().form_valid(form)


def folder_delete(request, pk=None):
    if not pk:
        messages.info(request, "Delete, No ID", extra_tags='alert-warning')
    folder = Folder.objects.filter(id=pk).first()
    if not folder:
        messages.info(request, f"Delete, No {pk} folder", extra_tags='alert-warning')
        return redirect(reverse('folders:folder_list'))
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
            form.instance.tag = parent.tag
            form.instance.level = parent.level + 1
            self.success_url = reverse_lazy('folders:folder_detail', kwargs={'pk': parent.id})
        else: # New level 0 folder
            form.instance.user = self.request.user
        return super().form_valid(form)

def get_folder_tree(user=None, parent=None, folder=None):
    tree = []
    if folder:
        tree.append(folder)
        childs = get_folder_tree(parent=folder)
        tree.extend(childs)
        return tree
    if not parent :
        if user:
            roots = Folder.objects.filter(level=0, user=user)
        else:
            roots = Folder.objects.filter(level=0)
    else:
        roots = Folder.objects.filter(parent=parent)
    for root in roots:
        tree.append(root)
        childs = get_folder_tree(parent=root)
        tree.extend(childs)
    return tree

def folder_tree(request, user_id=None, folder_id=None, mode=None):
    user = None
    if user_id:
        user = User.objects.filter(id=user_id).first()
    folder = None
    if folder_id:
        folder = Folder.objects.filter(id=folder_id).first()
    parent = None
    if folder:
        if folder.parent:
            parent = folder.parent
    tree = get_folder_tree(user=user, folder=folder)

    shared = []
    shared_to_me = FolderShare.objects.filter(who=request.user)
    for share in shared_to_me:
        shared.append(share.folder)

    folders = Folder.objects.filter(user=request.user)
    i_share = FolderShare.objects.filter(folder__in=folders)

    groups = Group.objects.filter(creator=request.user)

    return render(request, "folders/folder_tree.html", {
        'tree': tree,
        'parent': parent,
        'current_folder': folder,
        'shared': shared,
        'i_share': i_share,
        'groups': groups,
        'mode': mode,
        })

class FolderList(LoginRequiredMixin, ListView) :
    model = Folder

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        folders = Folder.objects.filter(user=self.request.user, level=0)

        if 'tag' in self.kwargs :
            tag = self.kwargs['tag']
            folders = folders.filter(tag=tag)

        context['folder_tree'] = folders

        shared = []
        shared_to_me = FolderShare.objects.filter(who=self.request.user)
        for share in shared_to_me:
            shared.append(share)
        context['shared'] = shared

        i_share = FolderShare.objects.filter(folder__in=folders)
        context['i_share'] = i_share

        context['groups'] = Group.objects.filter(creator=self.request.user)
        return context

class FolderDetail(LoginRequiredMixin, DetailView) :
    model = Folder

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        folders = Folder.objects.filter(user=self.request.user, parent=self.object)

        if 'tag' in self.kwargs :
            tag = self.kwargs['tag']
            folders = folders.filter(tag=tag)

        context['folder_tree'] = folders

        i_share = FolderShare.objects.filter(folder__in=folders)
        context['i_share'] = i_share

        context['groups'] = Group.objects.filter(creator=self.request.user)
        return context
