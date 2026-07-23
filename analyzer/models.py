from django.db import models


class DownloadedFile(models.Model):
    filename = models.CharField(
        'Имя файла',
        max_length=255,
        unique=True,
    )
    content = models.TextField('Содержимое')
    downloaded_at = models.DateTimeField('Время скачивания')

    class Meta:
        verbose_name = 'Скачанный файл'
        verbose_name_plural = 'Скачанные файлы'
        ordering = ['-downloaded_at']

    def __str__(self):
        return self.filename
