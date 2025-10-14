from celery import shared_task
from paragliding.extentions import get_flight_data, igc_downloader
import time


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def get_pilot_flights_data(self, profile_url: str, pilot_id: int):
    print(f"Veri çekme işlemi başladı: {profile_url} for pilot_id: {pilot_id}")
    try:
        get_flight_data.main(profile_url, pilot_id)
        print(
            f"Veri başarıyla çekildi. Sonuç: {profile_url} for pilot_id: {pilot_id}")
        return {'status': 'success', 'profile_url': profile_url, 'pilot_id': pilot_id}
    except Exception as e:
        print(f"Hata oluştu: {e}")
        self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def download_igc_file_task(self, url: str):
    print(f"IGC indirme işlemi başladı: {url}")
    try:
        igc_downloader.main(url)
        return {'status': 'success', 'url': url}
    except Exception as e:
        print(f"IGC indirilirken hata oluştu: {url}, Hata: {e}")
        self.retry(exc=e)


@shared_task
def example(argument=""):
    for i in range(10):
        time.sleep(1)
        print("zamanlama:", i, argument)
