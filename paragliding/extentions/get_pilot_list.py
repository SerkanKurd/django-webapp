import requests
from bs4 import BeautifulSoup
import json


def get_pilots_data(page_num):
    url = f"https://www.ypforum.com/leonardo/pilots/world/alltimes/brand:all,cat:0,class:all,xctype:all,club:all,takeoff:all&sortOrder=bestDistance&comp=&page_num={page_num}"

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception:
        return ""

    if response.status_code != 200:
        raise Exception("Failed to retrieve the page")

    rows = soup.select('[class^="l_row"]')
    data = {}
    for row in rows:
        row_selecet = row.find("a").get("href")
        pilot_id = row_selecet.split(", 200,")[1].split(",")[
            0].replace("'", "")
        result = [pilot_id]
        tables = row.find_all("td")
        result = [table.text.replace("\xa0km", "") for table in tables]
        result.pop(0)
        data.update({pilot_id: result})
    return data


if __name__ == "__main__":
    data = {}
    page_num = 1
    while True:
        print("Page:", page_num)
        get_data = get_pilots_data(page_num)
        if not get_data:
            break
        data.update(get_data)
        page_num += 1
    
    with open("pilots_data.json", "w") as f:
        json.dump(data, f, indent=4)
    print("Data successfully written to pilots_data.json")
