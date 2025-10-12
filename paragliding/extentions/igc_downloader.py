from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import platform
import requests
from bs4 import BeautifulSoup


if platform.system() == "Windows" or platform.system() == "Darwin":
    from webdriver_manager.chrome import ChromeDriverManager


def setup():
    global download_dir
    download_dir = os.path.abspath("downloads")
    global driver
    # if os.path.exists(download_dir):
    #     files = os.listdir(download_dir)
    #     for file in files:
    #         os.remove(os.path.join(download_dir, file))
    #         print(file, "deleted")
    # os.makedirs(download_dir, exist_ok=True)

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
            download_link = wait.until(
                EC.element_to_be_clickable((By.ID, "igcLink")))
            time.sleep(0.5)
            download_link.click()
            time.sleep(0.5)
            break
    return


def get_igc_files(igc_links: list) -> list[str]:
    before_download = os.listdir(download_dir)
    after_download = []
    for igc_link in igc_links:
        print(f"Start: {igc_link}")
        if igc_link:
            try:
                download_igc_file(igc_link)
                print(f"Finished: {igc_link}")
            except Exception:
                download_igc_file(igc_link)
                print(f"Failed!: {igc_link}")
                continue
    driver.quit()
    after_download = os.listdir(download_dir)
    downloaded_files = [
        file for file in after_download if file not in before_download]
    print(downloaded_files)
    return downloaded_files


def get_igc_links(url: str) -> dict[str, list[str]]:
    data = {}
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    if response.status_code != 200:
        raise Exception("Failed to retrieve the page")

    rows = soup.select('[class^="l_row"]')
    for row in rows:
        # Use select_one to get a single element, as .select() returns a list.
        pilot_name_element = row.select_one('.pilotLink')
        takeoff_name_element = row.select_one('.takeoffLink')
        date_element = row.select_one('.dateString')
        pilot_name = pilot_name_element.get_text(strip=True)
        takeoff_name = takeoff_name_element.get_text(strip=True)
        flight_link = f"https://www.ypforum.com/leonardo/flight/{int(
            row.get("id").replace("row_", "").strip())}"
        flight_date = date_element.get_text(strip=True).replace("/", ".")

        data[flight_link] = [pilot_name, takeoff_name, flight_date]
    return data


def main(url: str = "",
         *,
         download_links: list = [],
         download_limit: int = 10
         ) -> list[str]:
    if not url and not download_links:
        raise ValueError("URL ve indirme bağlantıları boş olamaz.")
    if url:
        download_links = list(get_igc_links(url).keys())
    if len(download_links) > download_limit:
        download_links = download_links[:download_limit]

    setup()
    downloaded_files = get_igc_files(download_links)
    return downloaded_files


if __name__ == "__main__":
    # url = "https://www.ypforum.com/leonardo/tracks/world/2025.05/brand:all,cat:1,class:all,xctype:all,club:all,pilot:0_6573,takeoff:all"
    # url = "https://www.ypforum.com/leonardo/tracks/world/alltimes/"
    url="https://www.ypforum.com/leonardo/tracks/world/2025.10.02/brand:all,cat:0,class:all,xctype:all,club:all,pilot:0_0,takeoff:all"
    print(main(url))
