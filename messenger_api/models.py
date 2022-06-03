from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class Messages(BaseModel):
    id = models.AutoField(primary_key=True, unique=True)
    content = models.CharField(max_length=10000)
    subject = models.CharField(max_length=2000)
    date = models.DateTimeField(auto_now_add=True, auto_now=False, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='receiver')
    sender = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='sender')

    def __str__(self):
        return f"Subject: {self.subject}\n" \
               f"Content: {self.content}"


class Inbox(BaseModel):
    id = models.AutoField(primary_key=True, unique=True)
    read = models.BooleanField(default=False)
    receiver = models.ForeignKey(User, on_delete=models.RESTRICT)
    message = models.ForeignKey(Messages, on_delete=models.RESTRICT)


class Outbox(BaseModel):
    id = models.AutoField(primary_key=True, unique=True)
    sender = models.ForeignKey(User, on_delete=models.RESTRICT)
    message = models.ForeignKey(Messages, on_delete=models.RESTRICT)
