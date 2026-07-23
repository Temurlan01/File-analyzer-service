import io
import time
import zipfile
import requests
from datetime import datetime, timezone, timedelta
from django.conf import settings
from .models import DownloadedFile


def download_all_files():
    api_base = getattr(settings, 'TARGET_API_BASE', 'http://91.199.149.128:18001').rstrip('/')
    candidate_id = getattr(settings, 'TARGET_CANDIDATE_ID', None)

    headers = {}
    if candidate_id:
        headers['X-Candidate-Id'] = candidate_id

    session = requests.Session()
    session.headers.update(headers)

    total_names_received = 0
    total_downloaded_count = 0

    nsk_tz = timezone(timedelta(hours=7))
    start_time_nsk = datetime.now(nsk_tz).strftime('%Y-%m-%d %H:%M:%S')

    while True:
        while True:
            resp = session.get(f"{api_base}/api/files/names")

            if resp.status_code in (429, 403):
                retry_after = int(resp.headers.get('Retry-After', 5))
                time.sleep(retry_after)
                continue

            resp.raise_for_status()
            break

        data = resp.json()

        if isinstance(data, dict):
            names = data.get('file_names', [])
        elif isinstance(data, list):
            names = data
        else:
            names = []

        if not names:
            break

        total_names_received += len(names)

        for i in range(0, len(names), 3):
            batch = names[i:i + 3]

            while True:
                time.sleep(1.5)

                dl_resp = session.post(
                    f"{api_base}/api/files/download",
                    json={"file_names": batch}
                )

                if dl_resp.status_code in (429, 403):
                    retry_after = int(dl_resp.headers.get('Retry-After', 5))
                    time.sleep(retry_after)
                    continue

                if not dl_resp.ok:
                    raise Exception(f"Ошибка {dl_resp.status_code} при скачивании {batch}: {dl_resp.text}")

                with zipfile.ZipFile(io.BytesIO(dl_resp.content)) as z:
                    for filename in z.namelist():
                        content_str = z.read(filename).decode('utf-8', errors='ignore')
                        now_nsk = datetime.now(nsk_tz)

                        DownloadedFile.objects.update_or_create(
                            filename=filename,
                            defaults={
                                'content': content_str,
                                'downloaded_at': now_nsk,
                            }
                        )
                        total_downloaded_count += 1
                break

            while True:
                time.sleep(1.5)

                ack_resp = session.post(
                    f"{api_base}/api/files/downloaded",
                    json={"file_names": batch}
                )

                if ack_resp.status_code in (429, 403):
                    retry_after = int(ack_resp.headers.get('Retry-After', 5))
                    time.sleep(retry_after)
                    continue

                if not ack_resp.ok:
                    raise Exception(f"Ошибка {ack_resp.status_code} при отметке {batch}: {ack_resp.text}")

                break

    return {
        'start_time_nsk': start_time_nsk,
        'names_received': total_names_received,
        'downloaded_count': total_downloaded_count
    }