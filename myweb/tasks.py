from celery import shared_task
from paragliding import get_from_ypforum
import time


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def get_pilot_flights_data(self, profil_url, pilot_id):
    print(f"Veri çekme işlemi başladı: {profil_url}")
    try:
        get_from_ypforum.main(profil_url)
        print(f"Veri başarıyla çekildi. Sonuç: {profil_url}")
        return {'status': 'success', 'profil_url': profil_url}
    except Exception as e:
        print(f"Hata oluştu: {e}")
        self.retry(exc=e)
        return {'status': 'error', 'message': str(e)}


@shared_task
def example(argument=""):
    for i in range(10):
        time.sleep(1)
        print("zamanlama:", i, argument)
