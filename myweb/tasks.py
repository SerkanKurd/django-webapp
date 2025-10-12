from celery import shared_task
from paragliding.extentions import get_ypforum
import time


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def get_pilot_flights_data(self, profile_url, pilot_id):
    print(f"Veri çekme işlemi başladı: {profile_url}")
    try:
        get_ypforum.main(profile_url)
        print(f"Veri başarıyla çekildi. Sonuç: {profile_url}")
        return {'status': 'success', 'profile_url': profile_url}
    except Exception as e:
        print(f"Hata oluştu: {e}")
        self.retry(exc=e)
        return {'status': 'error', 'message': str(e)}


@shared_task
def example(argument=""):
    for i in range(10):
        time.sleep(1)
        print("zamanlama:", i, argument)
