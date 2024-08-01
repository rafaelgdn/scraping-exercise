import json
import re
from unicodedata import normalize
from bs4 import BeautifulSoup
import asyncio
import nodriver as uc

links = [
  "https://www.heb.com/store-locations?address=%20Dallas&page=1",
  "https://www.heb.com/store-locations?address=%20Fort%20Worth&page=1"
]

days = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday"
]

response = []

# I had to open the browser to fetch the page content because the content is dynamically generated by JavaScript.
# This means that the data is loaded and rendered by the client-side scripts after the initial page load.
async def main():
    browser = await uc.start()

    for link in links:
        page = await browser.get("https://www.heb.com/store-locations?address=%20Dallas&page=1")

        await page.find("Find a Store", best_match=True)

        heb_page = BeautifulSoup(await page.get_content(), 'html.parser')

        ul_pagination = heb_page.css.select("ul[aria-label='Pagination Navigation']")
        pagination_li_elements = ul_pagination[0].find_all("li")
        last_pagination_li_elements = pagination_li_elements[-1]
        
        for i in range(1, int(last_pagination_li_elements.text) + 1):
            page_paginated = await browser.get(link.replace("page=1", f"page={i}"))

            await page_paginated.find("Find a Store", best_match=True)

            heb_page_paginated = BeautifulSoup(await page_paginated.get_content(), 'html.parser')

            store_cards = heb_page_paginated.css.select("ol[data-qe-id='findStoreCardContainer'] li")

            for store_card in store_cards:
                store = extract_store_info(store_card)
                response.append(store)

    browser.stop()

    
    with open("heb/heb.json", "w", encoding='utf8') as file:
        json.dump(response, file, indent=4, ensure_ascii=False)


def extract_store_info(store_card):
    encoded_name = store_card.find("h2").text

    store = {
        'name': normalize('NFKD', encoded_name),
        'address': store_card.css.select("span[data-qe-id='findStoreAddress']")[0].text,
        'phone_number': store_card.css.select("a[data-qe-id='findStorePhoneNumber']")[0].text,
        'Hours': extract_store_hours(store_card)
    }
    return store


def extract_store_hours(store_card):
    store_hours = store_card.css.select("p[data-qe-id='findStoreHours']")[0].text
    store_hours_pattern = r'(\d{1,2}:\d{2})\s*(AM|PM)\s*-\s*(\d{1,2}:\d{2})\s*(AM|PM)'
    match = re.search(store_hours_pattern, store_hours)
    open_hour = match.group(1)
    open_am_pm = match.group(2)
    close_hour = match.group(3)
    close_am_pm = match.group(4)

    hours = {}
    for day in days:
        hours[day] = {
            'open': f"{open_hour} {open_am_pm}",
            'close': f"{close_hour} {close_am_pm}"
        }
    return hours

asyncio.run(main())




