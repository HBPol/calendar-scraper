from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from ics import Calendar, Event
import time

def fetch_calendar_events_with_selenium(url):
    """Fetch calendar events from the given URL using Selenium."""
    try:
        # Set up Selenium WebDriver
        firefox_options = Options()
        firefox_options.add_argument("--headless")  # Run in headless mode
        firefox_options.add_argument("--disable-gpu")

        service = Service("/snap/bin/geckodriver")  # Update this to your GeckoDriver path
        driver = webdriver.Firefox(service=service, options=firefox_options)

        driver.get(url)

        # Wait for the page to load JavaScript content
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "event-item"))  # Update class as per page structure
        )

        # Extract page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        # Parse events from the HTML content
        events = []
        for event_item in soup.select('.event-item'):  # Modify this selector as per the page structure
            title_element = event_item.select_one('.event-title')
            date_element = event_item.select_one('.event-date')
            time_element = event_item.select_one('.event-time')

            if not (title_element and date_element and time_element):
                print("Skipping an event due to missing data.")
                continue

            title = title_element.get_text(strip=True)
            date = date_element.get_text(strip=True)
            time = time_element.get_text(strip=True)
            location = event_item.select_one('.event-location').get_text(strip=True) if event_item.select_one('.event-location') else ""

            events.append({
                'title': title,
                'date': date,
                'time': time,
                'location': location
            })

        return events
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return []

def save_to_google_calendar_format(events, output_file):
    """Save events to a file in ICS format for Google Calendar import."""
    calendar = Calendar()

    for event in events:
        ics_event = Event()
        ics_event.name = event['title']
        ics_event.begin = f"{event['date']} {event['time']}"
        ics_event.location = event['location']
        calendar.events.add(ics_event)

    with open(output_file, 'w') as file:
        file.writelines(calendar.serialize_iter())

if __name__ == "__main__":
    # Define the URL of the calendar page
    url = "https://www.queenemmaschool.org.uk/calendar/?calid=2&pid=16&viewid=2"

    # Fetch events using Selenium
    events = fetch_calendar_events_with_selenium(url)

    if events:
        print(f"Fetched {len(events)} events. Saving to file...")
        save_to_google_calendar_format(events, 'calendar_events.ics')
        print("Events saved to 'calendar_events.ics'. You can now import this file into your Google Calendar.")
    else:
        print("No events found or failed to fetch events.")
