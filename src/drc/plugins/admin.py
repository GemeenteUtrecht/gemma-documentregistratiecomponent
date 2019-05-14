from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .models import StorageConfig


@admin.register(StorageConfig)
class StorageConfigAdmin(SingletonModelAdmin):
    pass
