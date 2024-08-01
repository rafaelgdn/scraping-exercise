import json
from bs4 import BeautifulSoup
import asyncio
import nodriver as uc

links = [
  "https://www.starbucks.com/store-locator?map=32.80305,-96.813205,13z&place=dallas",
  "https://www.starbucks.com/store-locator?map=32.76194,-97.323635,12z&place=Fort%20Worth"
]

response = []

async def main():
  browser = await uc.start()

  for link in links:
    page = await browser.get(link)

    try:
      consentButton = await page.select("#truste-consent-button")
      if consentButton:
        await consentButton.mouse_click()
    except:
      pass

    searchButton = await page.select("button[aria-label='Submit search term']")
    await searchButton.mouse_click()
    
    cards = await page.select_all("a[href='/store-locator/store/']")

    for card in cards:
      await card.click()

      starbucks_page = BeautifulSoup(await page.get_content(), 'html.parser')

      expanded_card = starbucks_page.css.select("article[aria-labelledby='expandedLocationCardLabel'] section div")
      adress_one = expanded_card[0].next_sibling.find_all("span")[0].text
      adress_two = expanded_card[0].next_sibling.find_all("span")[1].text

      store = {
        'name': starbucks_page.css.select("article[aria-labelledby='expandedLocationCardLabel'] h2")[0].text,
        'address': f"{adress_one}, {adress_two}",
        'phone_number': expanded_card[0].next_sibling.find_all("span")[4].text,
        'Hours': {},
        'options': [],
        'amenities': []
      }

      schedule = starbucks_page.css.select("ul[data-e2e='store-schedule']")

      if schedule: 
        li_schedule = schedule[0].find_all("li")

        for li in li_schedule:
          scheduleDay = li.css.select("span[class*='scheduleDay']")[0].text
          scheduleHours = li.css.select("span[class*='scheduleHours']")[0].text

          store['Hours'][scheduleDay] = {
            'open': scheduleHours if scheduleHours == 'Closed' else scheduleHours.split(" to ")[0],
            'close': scheduleHours if scheduleHours == 'Closed' else scheduleHours.split(" to ")[1]
          }

        options_section = starbucks_page.css.select("article[aria-labelledby='expandedLocationCardLabel'] section")[2].find("ul")

        if options_section:
          options = options_section.find_all("li")
          for option in options:
            if option.find("svg"):
              store['options'].append(option.find("svg").next_sibling.text)

        amenities_section = starbucks_page.css.select("article[aria-labelledby='expandedLocationCardLabel'] section")[3].find("ul")

        if amenities_section:
          amenities = amenities_section.find_all("li")
          for amenity in amenities:
            if amenity.find("svg"):
              store['amenities'].append(amenity.find("svg").next_sibling.text)

        response.append(store)

        try:
          closeButton = await page.select("button[aria-label='Close']")
          await closeButton.click()
        except:
          pass
  
  browser.stop()

  with open("starbucks/starbucks.json", "w", encoding='utf8') as file:
        json.dump(response, file, indent=4, ensure_ascii=False)



asyncio.run(main())