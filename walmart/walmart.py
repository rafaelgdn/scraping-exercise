import requests
import json
import re
from bs4 import BeautifulSoup


def get_store_info(market_link, headers):
    store = {
        'name': market_link.text,
        'address': f"{market_link.next_sibling.text}, {market_link.next_sibling.next_sibling.text}",
        'phone_number': market_link.next_sibling.next_sibling.next_sibling.text,
        'Hours': {},
        'services': [],
        'url': f"https://www.walmart.com{market_link['href']}"
    }

    request_text = requests.get(store['url'], headers=headers).text
    walmart_store_page = BeautifulSoup(request_text, 'html.parser')

    is_page_active = walmart_store_page.find("h3", string="Store Info")

    if not is_page_active:
        return None

    sensory_friendly_text = walmart_store_page.find("h4", string="Sensory-friendly hours").next_sibling.next_sibling.text
    sensory_friendly_hours = re.findall(r"(\d+)am", sensory_friendly_text)
    open_hour = sensory_friendly_hours[0]
    close_hour = sensory_friendly_hours[1]

    for day in days:
        store['Hours'][day] = {
            'open': f"{open_hour}:00 AM",
            'close': f"{close_hour}:00 AM"
        }

    all_services_element = walmart_store_page.find("h3", string="Store services").find_next_siblings()

    for service_element in all_services_element[:-1]:
        store['services'].append(service_element.i.next_sibling.text)

    return store


def fetch_store_data(links, headers):
    response = []

    for link in links:
        request_text = requests.get(link, headers=headers).text
        walmart_page = BeautifulSoup(request_text, 'html.parser')

        market_links = walmart_page.css.select("a[href*='/store/']")

        for market_link in market_links[:-1]:
            store_info = get_store_info(market_link, headers)

            if store_info:
                response.append(store_info)

    return response


if __name__ == "__main__":
    links = [
        "https://www.walmart.com/store-directory/tx/fort%20worth",
        "https://www.walmart.com/store-directory/tx/dallas"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    store_data = fetch_store_data(links, headers)

    with open("walmart/walmart.json", "w") as file:
        json.dump(store_data, file, indent=4)