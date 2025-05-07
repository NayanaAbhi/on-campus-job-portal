import requests
from icalendar import Calendar
from datetime import datetime
from dateutil import tz

def fetch_canvas_events(ics_url):
    events = []
    try:
        response = requests.get(ics_url)
        response.raise_for_status()

        cal = Calendar.from_ical(response.content)
        for component in cal.walk():
            if component.name == "VEVENT":
                event = {
                    "title": str(component.get("summary")),
                    "start": component.get("dtstart").dt,
                    "end": component.get("dtend").dt,
                }
                # Normalize naive datetimes to local timezone
                if isinstance(event["start"], datetime) and event["start"].tzinfo is None:
                    event["start"] = event["start"].replace(tzinfo=tz.tzlocal())
                if isinstance(event["end"], datetime) and event["end"].tzinfo is None:
                    event["end"] = event["end"].replace(tzinfo=tz.tzlocal())

                events.append(event)
    except Exception as e:
        print(f"Failed to fetch .ics: {e}")
    return events
