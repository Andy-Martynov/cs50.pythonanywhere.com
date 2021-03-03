from django.db import models
from django.urls import reverse

from account.models import User, Group

class Message(models.Model) :
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reciever")
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     ordering = ["-created"]

    def __str__(self):
        return f"{self.id} {self.sender.username} to {self.reciever.username} created {self.created}"

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender.serialize(),
            "reciever": self.reciever.serialize(),
            "text": self.text,
            'created': self.created.strftime("%d.%m.%y %X"),
        }

class GroupMessage(models.Model) :
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_sender")
    reciever = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group")
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.id} {self.sender.username} to {self.reciever.name} created {self.created}"

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender.serialize(),
            "reciever": self.reciever.serialize(),
            "text": self.text,
            'created': self.created.strftime("%d.%m.%y %X"),
        }

class Unread(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="unread_user")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="unread_sender")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True, related_name="unread_group")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        if self.sender:
            return f"{self.id} {self.user.username}'s unread from sender <{self.sender.username}> set {self.created}"
        else:
            return f"{self.id} {self.user.username}'s unread from group <{self.group.name}> set {self.created}"

    def serialize(self):
        if self.sender:
            return {
                "id": self.id,
                'mode': 'sender',
                "sender": self.sender.serialize(),
                'created': self.created.strftime("%d.%m.%y %X"),
            }
        else:
            return {
                "id": self.id,
                'mode': 'group',
                "group": self.group.serialize(),
                'created': self.created.strftime("%d.%m.%y %X"),
            }




