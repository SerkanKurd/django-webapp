from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import platform
from django.shortcuts import render
from paragliding import models


if platform.system() == "Windows" or platform.system() == "Darwin":
    from webdriver_manager.chrome import ChromeDriverManager


def setup():
    global download_dir
    download_dir = os.path.abspath("downloads")
    global driver

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    if platform.system() == "Windows" or platform.system() == "Darwin":
        driver = webdriver.Chrome(options=options, service=Service(
            ChromeDriverManager().install()))
    else:
        driver = webdriver.Chrome(
            service=Service("/usr/bin/chromedriver"),
            options=options
        )
    return driver


def download_igc_file(url: str):
    print(f"Downloading: {url}")
    setup()
    driver.get(url)
    try:
        wait = WebDriverWait(driver, 10)
        igc_download_pos = wait.until(
            EC.element_to_be_clickable((By.ID, "IgcDownloadPos")))
        igc_download_pos.click()
    except Exception as e:
        print(f"IgcDownloadPos butonu bulunamadı veya tıklanamadı: {e}")
        return

    iframe = wait.until(EC.presence_of_element_located(
        (By.ID, "IgcDownloadFrame")))
    driver.switch_to.frame(iframe)

    target_element = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id='captchaWrapper']/div[5]/div")))
    target = target_element.value_of_css_property("background-position")
    target = target.split("px ")[0]

    draggable_objects = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "[id^='draggable']")))
    for obj in draggable_objects:
        obj_pos = obj.value_of_css_property(
            "background-position").split("px ")[0]
        if target == obj_pos:
            obj.click()
            time.sleep(0.5)
            download_link = wait.until(
                EC.element_to_be_clickable((By.ID, "igcLink")))
            time.sleep(0.5)
            download_link.click()
            time.sleep(0.5)
            break
    driver.quit()
    print(f"Finish: {url}")
    return


def dosya_yukle(request):
    if request.method == 'POST' and 'dosya' in request.FILES:
        yuklenen_dosya = request.FILES['dosya']

        # Dosyayı ikili modda oku
        dosya_icerigi = yuklenen_dosya.read()

        # Modeli oluştur ve kaydet
        yeni_kayit = UrunResmi(
            urun_adi="Örnek Ürün",
            dosya_icerigi=dosya_icerigi,
            dosya_adi=yuklenen_dosya.name,
            dosya_tipi=yuklenen_dosya.content_type
        )
        yeni_kayit.save()
        return render(request, 'basarili_sayfa.html')

    return render(request, 'yukleme_formu.html')


def find_pilots():
    pilots = models.Pilot.objects.filter(is_updated=False)
    print(pilots)


if __name__ == "__main__":
    url = "https://www.ypforum.com/leonardo/flight/178354"
    # download_igc_file(url)
    find_pilots()
