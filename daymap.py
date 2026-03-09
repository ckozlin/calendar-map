import webbrowser
from calendar_client import get_todays_events
from geocode import geocode
from map_builder import build_map
import time


def main():
    raw_events = get_todays_events()

    events = []

    for e in raw_events:
        location = e.get("location")

        if not location:
            continue

        coords = geocode(location)
        time.sleep(1)

        print("Geocoding:", location)
        print("Coords:", coords)

        if not coords:
            continue

        events.append(
            {
                "summary": e.get("summary"),
                "coords": coords
            }
        )

    build_map(events)

    webbrowser.open("calendar_map.html")


if __name__ == "__main__":
    main()