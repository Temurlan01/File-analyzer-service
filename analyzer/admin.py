from django.contrib import admin

from analyzer.models import DownloadedFile


@admin.register(DownloadedFile)

class DownloadedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'filename', 'downloaded_at')
