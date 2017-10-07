from django.db import models

# Create your models here.
from django.db.models import Model, CharField, AutoField


class Poll(Model):
    id = AutoField(primary_key=True)

    title = CharField(max_length=255, null=True, blank=True)