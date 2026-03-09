import webbrowser
from calendar_client import get_events_for_day
from geocode import geocode
from map_builder import build_map
import time
import argparse
from datetime import datetime, timedelta

def parse_date(date_str):
    if date_str == "today":
        return datetime.today().date()

    if date_str == "tomorrow":
        return datetime.today().date() + timedelta(days=1)

    return datetime.strptime(date_str, "%Y-%m-%d").date()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="today")
    parser.add_argument("--calendar", default="primary")
    parser.add_argument("--timezone", default="utc")

    args = parser.parse_args()

    target_date = parse_date(args.date)

    raw_events = get_events_for_day(target_date, args.calendar)

    events = []

    for e in raw_events:
        print(e["summary"], e["start"])
        location = e.get("location")
        start = e["start"].get("dateTime", e["start"].get("date"))

        time_str = start.split("T")[1][:5] if "T" in start else "All Day"

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
                "time": time_str,
                "coords": coords
            }
        )

    build_map(events, args.date)

    # webbrowser.open(f"calendar_map/calendar_map_{args.date}.html")


if __name__ == "__main__":
    main()