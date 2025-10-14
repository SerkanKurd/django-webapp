# from paragliding import models
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal, InvalidOperation


def get_page(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    if response.status_code != 200:
        raise Exception("Failed to retrieve the page")

    rows = soup.select('[class^="flightShowBox"]')

    if soup.find("div").text == "No such flight exists":
        print(f"Flight {url} not exists")
        return

    data = ""
    for row in rows:
        data += row.text

    data = data.replace("\xa0", "").strip().split("\n")
    try:
        flightdata = {}
        flightdata["pilot_name"] = data[0].split(
            " Tarih: ")[0].replace("Pilot: ", "")
        flightdata["flight_date"] = data[0].split(" Tarih: ")[1]
        flightdata["takeOffTime"] = data[15]
        flightdata["landingTime"] = data[22]
        flightdata["duration"] = data[81]
        flightdata["takeoff_name"] = data[18]
        flightdata["landing_name"] = data[25]
        flightdata["distance"] = data[35]
        flightdata["distance_max"] = data[41]
        flightdata["distance_olc"] = data[47]
        flightdata["points_olc"] = data[51]
        flightdata["points_olc_type"] = data[55]
        flightdata["paraglider"] = data[70]
        flightdata["vario_max"] = data[85]
        flightdata["vario_min"] = data[89]
        flightdata["altitude_max"] = data[93]
        flightdata["altitute_min"] = data[97]
        flightdata["altitude_takeoff"] = data[101]
        flightdata["altitute_gain"] = data[105]
        flightdata["speed_max"] = data[109]
        flightdata["speed_avarage"] = data[113]
    except Exception as e:
        print(f"Unexpected error on page {url}: {e}")
    return flightdata


def check_data(flightdata):
    date_str = data['flight_date'].replace('/', '.')
    try:
        native_date = datetime.strptime(date_str, '%d.%m.%Y')
        flight_date = timezone.make_aware(
            native_date, timezone=timezone.get_current_timezone())
    except ValueError:
        print(
            f"Could not parse flight date for flight {flight_id}: {e}."
            f"Skipping. ({date_str})")
        duration = None
        continue


def main(flight_url: str):
    pass


if __name__ == "__main__":
    data = get_page("https://www.ypforum.com/leonardo/flight/154136")
    text = ""
    for key, value in data.items():
        text += f"{key}: {value}\n"
    print(text)
