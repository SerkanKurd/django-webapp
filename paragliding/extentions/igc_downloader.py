from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import platform
import shutil
from django.shortcuts import render
from paragliding import models


if platform.system() == "Windows" or platform.system() == "Darwin":
    from webdriver_manager.chrome import ChromeDriverManager


def setup():
    global driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
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

    print(f"Finish: {url}")
    return upload_file(url)


def upload_file(url):
    print("Uploading file to DB")
    file = ""
    for _ in range(5):
        files = os.listdir(download_dir)
        if not files:
            time.sleep(1)
            continue
        if len(files) > 1:
            return
        file = files[0]
        if file.endswith(".crdownload"):
            time.sleep(5)
        else:
            break

    if not file or not file.lower().endswith(".igc"):
        print(f"File not found or not an IGC file: '{file}'")
        return
    flight_data = models.FlightData.objects.get(flight_url=url)
    flight_data.file_name = file
    with open(os.path.join(download_dir, file), "rb") as f:
        flight_data.file_content = f.read()
    flight_data.save()
    print(f"File uploaded to DB: {file}")
    return


def main(url: str):
    global download_dir
    flight_id = url.split("/")[-1]
    download_dir = os.path.abspath(f"downloads/{flight_id}")
    shutil.rmtree(download_dir, ignore_errors=True)
    os.mkdir(download_dir)
    setup()

    try:
        flight_data = models.FlightData.objects.get(flight_url=url)
        if flight_data.file_content:
            print(f"File for {url} already exists in DB. Skipping.")
            return

        download_igc_file(url)
    except Exception as e:
        print(f"An error occurred during IGC download for {url}: {e}")
        raise  # Re-raise the exception to allow Celery to retry
    finally:
        shutil.rmtree(download_dir, ignore_errors=True)
        driver.quit()


if __name__ == "__main__":
    url = "https://www.ypforum.com/leonardo/flight/178354"
    main(url)
