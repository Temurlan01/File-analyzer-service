from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock
import zipfile
import io
from .models import DownloadedFile
from .services import download_all_files


class DownloadedFileModelTest(TestCase):
    def test_create_file(self):
        file = DownloadedFile.objects.create(
            filename='test.txt',
            content='1234567890',
            downloaded_at=timezone.now()
        )
        self.assertEqual(file.filename, 'test.txt')
        self.assertEqual(file.content, '1234567890')
        self.assertIsInstance(file.downloaded_at, timezone.datetime)

    def test_unique_filename(self):
        DownloadedFile.objects.create(
            filename='test.txt',
            content='12345',
            downloaded_at=timezone.now()
        )
        with self.assertRaises(Exception):
            DownloadedFile.objects.create(
                filename='test.txt',
                content='67890',
                downloaded_at=timezone.now()
            )

    def test_ordering(self):
        file1 = DownloadedFile.objects.create(
            filename='file1.txt',
            content='1',
            downloaded_at=timezone.now() - timedelta(hours=2)
        )
        file2 = DownloadedFile.objects.create(
            filename='file2.txt',
            content='2',
            downloaded_at=timezone.now() - timedelta(hours=1)
        )
        files = list(DownloadedFile.objects.all())
        self.assertEqual(files[0], file2)
        self.assertEqual(files[1], file1)


class DownloadServiceTest(TestCase):
    @patch('analyzer.services.requests.Session')
    def test_download_all_files_empty_response(self, mock_session_class):
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_session.get.return_value = mock_response
        
        result = download_all_files()
        
        self.assertEqual(result['names_received'], 0)
        self.assertEqual(result['downloaded_count'], 0)
        mock_session.get.assert_called_once()

    @patch('analyzer.services.requests.Session')
    def test_rate_limiting_429(self, mock_session_class):
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {'Retry-After': '5'}
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = []
        
        mock_session.get.side_effect = [mock_response_429, mock_response_200]
        
        with patch('analyzer.services.time.sleep'):
            download_all_files()
        
        self.assertEqual(mock_session.get.call_count, 2)

    @patch('analyzer.services.requests.Session')
    def test_download_with_files(self, mock_session_class):
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Create ZIP file content
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr('file1.txt', '12345')
            zip_file.writestr('file2.txt', '67890')
        zip_content = zip_buffer.getvalue()
        
        # Mock GET /api/files/names - return empty after first call to stop loop
        mock_names_response = Mock()
        mock_names_response.status_code = 200
        mock_names_response.json.return_value = ['file1.txt', 'file2.txt']
        
        mock_empty_response = Mock()
        mock_empty_response.status_code = 200
        mock_empty_response.json.return_value = []
        
        mock_session.get.side_effect = [mock_names_response, mock_empty_response]
        
        # Mock POST /api/files/download
        mock_download_response = Mock()
        mock_download_response.status_code = 200
        mock_download_response.content = zip_content
        mock_download_response.raise_for_status = Mock()
        
        # Mock POST /api/files/downloaded
        mock_ack_response = Mock()
        mock_ack_response.status_code = 200
        mock_ack_response.raise_for_status = Mock()
        
        mock_session.post.side_effect = [mock_download_response, mock_ack_response]
        
        result = download_all_files()
        
        self.assertEqual(result['names_received'], 2)
        self.assertEqual(result['downloaded_count'], 2)
        self.assertEqual(DownloadedFile.objects.count(), 2)


class CalculateStatsTest(TestCase):
    def setUp(self):
        DownloadedFile.objects.create(
            filename='file1.txt',
            content='12345',
            downloaded_at=timezone.now()
        )
        DownloadedFile.objects.create(
            filename='file2.txt',
            content='67890',
            downloaded_at=timezone.now()
        )

    def test_calculate_stats(self):
        from analyzer.views import CalculateStatsView
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        view = CalculateStatsView.as_view()
        
        request = factory.post('/api/calculate/', {
            'filenames': ['file1.txt', 'file2.txt'],
            'select_all_in_db': False
        })
        
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        self.assertIn('global_stats', data)
        self.assertIn('file_stats', data)
        self.assertEqual(data['processed_files_count'], 2)
        
        # Check that each digit 0-9 is counted
        for digit in map(str, range(10)):
            self.assertIn(digit, data['global_stats'])

    def test_calculate_stats_select_all(self):
        from analyzer.views import CalculateStatsView
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        view = CalculateStatsView.as_view()
        
        request = factory.post('/api/calculate/', {
            'select_all_in_db': True
        })
        
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['processed_files_count'], 2)

    def test_calculate_stats_no_files(self):
        from analyzer.views import CalculateStatsView
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        view = CalculateStatsView.as_view()
        
        request = factory.post('/api/calculate/', {
            'filenames': [],
            'select_all_in_db': False
        })
        
        response = view(request)
        
        self.assertEqual(response.status_code, 400)

