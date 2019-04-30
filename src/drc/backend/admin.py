from django.contrib import admin

from .models import DjangoStorage


@admin.register(DjangoStorage)
class DjangoStorageAdmin(admin.ModelAdmin):
    # list_display = ('', )
    pass
