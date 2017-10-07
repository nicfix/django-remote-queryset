from django.contrib import admin

# Register your models here.
from polls.models import Poll

admin.site.register(Poll)
