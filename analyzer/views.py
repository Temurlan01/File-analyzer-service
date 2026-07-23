import requests
from django.conf import settings
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DownloadedFile
from .serializers import CalculateRequestSerializer, DownloadedFileSerializer
from .services import download_all_files


@method_decorator(csrf_exempt, name='dispatch')
class StartDownloadView(APIView):
    """Эндпоинт для запуска скачивания каталога"""

    @extend_schema(
        summary="Запустить скачивание файлов",
        responses={200: OpenApiTypes.OBJECT, 500: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        try:
            result = download_all_files()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileListView(APIView):
    """Эндпоинт для получения списка скачанных файлов с пагинацией"""

    @extend_schema(
        summary="Получить список скачанных файлов",
        parameters=[
            OpenApiParameter(
                name='page', type=int, description='Номер страницы', default=1
            ),
            OpenApiParameter(
                name='size', type=int, description='Размер страницы', default=10
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('size', 10))

        queryset = DownloadedFile.objects.all().order_by('-downloaded_at')
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        serializer = DownloadedFileSerializer(page_obj, many=True)

        return Response({
            'total_items': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'items': serializer.data,
        })


@method_decorator(csrf_exempt, name='dispatch')
class CalculateStatsView(APIView):
    """Эндпоинт для расчета статистики по цифрам в файлах"""

    @extend_schema(
        summary="Рассчитать статистику цифр",
        request=CalculateRequestSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = CalculateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        filenames = data.get('filenames')
        select_all_in_db = data.get('select_all_in_db')

        if select_all_in_db:
            files = DownloadedFile.objects.all()
        elif filenames:
            files = DownloadedFile.objects.filter(filename__in=filenames)
        else:
            return Response(
                {'error': 'Не выбраны файлы'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        global_stats = {str(digit): 0 for digit in range(10)}
        file_stats = {}

        for file_obj in files:
            current_file_stats = {str(digit): 0 for digit in range(10)}
            for char in file_obj.content:
                if char.isdigit():
                    current_file_stats[char] += 1
                    global_stats[char] += 1
            file_stats[file_obj.filename] = current_file_stats

        return Response({
            'global_stats': global_stats,
            'file_stats': file_stats,
            'processed_files_count': files.count(),
        })


@method_decorator(csrf_exempt, name='dispatch')
class ResetProgressView(APIView):
    """Сбросить прогресс скачивания кандидата"""

    @extend_schema(
        summary="Сбросить прогресс кандидата",
        responses={200: OpenApiTypes.OBJECT, 500: OpenApiTypes.OBJECT},
    )
    def delete(self, request, candidate_id):
        api_base = getattr(
            settings, 'TARGET_API_BASE', 'http://91.199.149.128:18001'
        ).rstrip('/')
        admin_token = getattr(settings, 'ADMIN_TOKEN', 'admin_secret_token')

        headers = {'X-Admin-Token': admin_token}

        try:
            resp = requests.delete(
                f'{api_base}/api/admin/candidates/{candidate_id}/progress',
                headers=headers,
            )
            resp.raise_for_status()
            return Response(resp.json(), status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ResetThrottlingView(APIView):
    """Снять бан и обнулить счётчики частоты запросов"""

    @extend_schema(
        summary="Снять ограничения (throttling) с IP",
        responses={200: OpenApiTypes.OBJECT, 500: OpenApiTypes.OBJECT},
    )
    def delete(self, request, client_ip):
        api_base = getattr(
            settings, 'TARGET_API_BASE', 'http://91.199.149.128:18001'
        ).rstrip('/')
        admin_token = getattr(settings, 'ADMIN_TOKEN', 'admin_secret_token')

        headers = {'X-Admin-Token': admin_token}

        try:
            resp = requests.delete(
                f'{api_base}/api/admin/clients/{client_ip}/throttling',
                headers=headers,
            )
            resp.raise_for_status()
            return Response(resp.json(), status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )