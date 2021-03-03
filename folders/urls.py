from django.urls import path
from . import views

app_name = 'folders'
urlpatterns = [
    path("", views.index, name="index"),

    path("create", views.FolderCreate.as_view(), name="folder_create"),
    path("create/<int:parent_id>", views.FolderCreate.as_view(), name="folder_create"),
    path("create/<int:link_id>/<str:mode>", views.FolderCreate.as_view(), name="folder_create"),

    path("share/<int:pk>", views.folder_share, name="folder_share"),
    path("add_share", views.add_share, name="add_share"),
    path("remove_share", views.remove_share, name="remove_share"),

    path("update/<int:pk>", views.FolderUpdate.as_view(), name="folder_update"),
    path("delete/<int:pk>", views.folder_delete, name="folder_delete"),
    path("detail/<int:pk>", views.FolderDetail.as_view(), name="folder_detail"),
    path("detail/<int:pk>/<str:tag>", views.FolderDetail.as_view(), name="folder_detail"),
    path("list", views.FolderList.as_view(), name="folder_list"),
    path("list/<str:tag>", views.FolderList.as_view(), name="folder_list"),

    path("folder_tree", views.folder_tree, name="folder_tree"),
    path("folder_tree/<int:user_id>", views.folder_tree, name="folder_tree"),
    path("folder_tree/<int:user_id>/<int:folder_id>", views.folder_tree, name="folder_tree"),
    path("folder_tree/<int:user_id>/<int:folder_id>/<str:mode>", views.folder_tree, name="folder_tree"),
]