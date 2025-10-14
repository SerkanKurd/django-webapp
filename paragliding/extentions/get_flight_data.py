import requests
from bs4 import BeautifulSoup
from paragliding import models
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal, InvalidOperation


def get_name(profile_url: str):
    try:
        response = requests.get(profile_url)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception:
        return ""

    if response.status_code != 200:
        raise Exception("Failed to retrieve the page")

    row = soup.find("b")
    if row:
        return row.get_text()
    return ""


def get_page_data(pilot_id, flights_url) -> dict[int, dict]:
    existing_flight_urls = set(models.FlightData.objects.filter(
        pilot_id=pilot_id).values_list('flight_url', flat=True))

    def data_clean(data):
        data = data.replace("\xa0", "")
        return data

    response = requests.get(flights_url)
    soup = BeautifulSoup(response.text, "html.parser")

    if response.status_code != 200:
        raise Exception("Failed to retrieve the page")

    rows = soup.select('[class^="l_row"]')
    if not rows:
        return {}

    flights_data = {}
    for row in rows:
        flight_data = {}
        flight_num = int(row.get("id").replace("row_", "").strip())
        data = [data.text for data in row.find_all(
            "td") if data.text != ""]
        data = list(map(data_clean, data))
        img_alt = [img.get("alt") for img in row.find_all("img")]
        flight_data = {flight_num:
                       {
                           "pilot_name": data[2].split("\n")[0],
                           "flight_date": data[1],
                           "takeoff_name": data[2].split("\n")[1],
                           "duration": data[3],
                           "distance": data[4],
                           "distance_olc": data[5],
                           "points_olc": data[6],
                           "country": img_alt[1],
                           "flight_type": img_alt[3],
                           "paraglider": img_alt[4],
                           "flight_url": f"https://www.ypforum.com/leonardo/flight/{flight_num}"
                       }
                       }
        if flight_data[flight_num]['flight_url'] in existing_flight_urls:
            return flights_data
        flights_data.update(flight_data)
    return flights_data


def get_flights_data(profile_url: str, pilot_id: int):
    ypforum_pilot_id = profile_url.split("/")[-1]
    fligts_data_all = {}
    page_num = 1
    while True:
        fligts_url = f"https://www.ypforum.com/leonardo/tracks/world/alltimes/brand:all,cat:0,class:all,xctype:all,club:all,pilot:{ypforum_pilot_id},takeoff:all&sortOrder=DATE&page_num={str(page_num)}"
        fligts_data = get_page_data(pilot_id, fligts_url)
        if not fligts_data:
            break
        fligts_data_all.update(fligts_data)
        print(f"Page {page_num} saved")
        page_num += 1
    return fligts_data_all


def fligts_data_to_db(fligts_data_all, pilot_id: int):
    for flight_id, data in fligts_data_all.items():
        try:
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

            try:
                hours, minutes = map(int, data['duration'].split(':'))
                duration = timedelta(hours=hours, minutes=minutes)
            except (ValueError, AttributeError) as e:
                print(
                    f"Could not parse duration for flight {flight_id}: {e}."
                    f"Skipping. ({data['duration']})")
                duration = None
                continue

            try:
                distance = Decimal(data['distance'].replace('km', ''))
            except (ValueError, InvalidOperation) as e:
                print(
                    f"Could not parse distance for flight {flight_id}: {e}."
                    f"Skipping. ({data['distance']})")
                distance = None

            try:
                distance_olc = Decimal(data['distance_olc'].replace('km', ''))
            except (ValueError, InvalidOperation) as e:
                print(
                    f"Could not parse distance_olc for flight {flight_id}: {e}."
                    f"Skipping. ({data['distance_olc']})")
                distance_olc = None

            try:
                points_olc = Decimal(data['points_olc'])
            except (ValueError, InvalidOperation) as e:
                print(
                    f"Could not parse points_olc for flight {flight_id}: {e}."
                    f"Skipping. ({data['points_olc']})")
                points_olc = None

        except (ValueError, TypeError, InvalidOperation, AttributeError) as e:
            print(
                f"Could not parse data for flight {flight_id}: {e}. Skipping.")
            continue
        # Create or update flight record
        models.FlightData.objects.update_or_create(
            flight_url=data['flight_url'],
            defaults={
                'pilot_id': pilot_id,
                'flight_date': flight_date,
                'takeoff_name': data['takeoff_name'],
                'duration': duration,
                'distance': distance,
                'distance_olc': distance_olc,
                'points_olc': points_olc,
                'country': data['country'],
                'flight_type': data['flight_type'],
                'paraglider': data['paraglider'],
            }
        )

    return print(f"Finished processing flights for pilot ID {pilot_id}.")


def main(profile_url: str, pilot_id: int):
    fligts_data_all = get_flights_data(profile_url, pilot_id)
    fligts_data_to_db(fligts_data_all, pilot_id)


if __name__ == "__main__":
    # print(get_name("https://www.ypforum.com/leonardo/pilot/0_6573"))
    # print(get_flight_data("0_6573"))
    print(get_flights_data("https://www.ypforum.com/leonardo/pilot/0_6573", 1))
