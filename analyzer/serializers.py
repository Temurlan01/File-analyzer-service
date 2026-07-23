from rest_framework import serializers
from .models import DownloadedFile


class DownloadedFileSerializer(serializers.ModelSerializer):
    """Сериализатор для списка файлов (выходные данные)"""
    downloaded_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = DownloadedFile
        fields = ['id', 'filename', 'downloaded_at']


class CalculateRequestSerializer(serializers.Serializer):
    """Сериализатор для валидации входящего запроса на расчет"""
    filenames = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=[]
    )
    select_all_in_db = serializers.BooleanField(required=False, default=False)