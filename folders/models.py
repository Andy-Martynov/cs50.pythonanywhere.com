from django.db import models

from account.models import User

class Folder(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="folders")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="subfolders")
    next = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name="prev_folder")
    prev = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name="next_folder")
    name = models.CharField(max_length=50, blank=True, null=True)
    level = models.IntegerField(default=0)
    tag = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class FolderShare(models.Model) :
    who = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_whom_share_i')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='shares_to_me')

    def __str__(self):
        return f"{self.folder.user.username} shares ({self.folder.id}) {self.folder} to {self.who.username}"



