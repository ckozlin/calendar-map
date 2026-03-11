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


def build_date_list(start_date, days=None, end_date=None):

    if days:
        return [start_date + timedelta(days=i) for i in range(days)]

    if end_date:
        dates = []
        d = start_date
        while d <= end_date:
            dates.append(d)
            d += timedelta(days=1)
        return dates

    return [start_date]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--date", default="today")
    parser.add_argument("--end-date")
    parser.add_argument("--days", type=int)

    parser.add_argument("--calendar", default="primary")
    parser.add_argument("--timezone", default="utc")

    args = parser.parse_args()

    start_date = parse_date(args.date)
    end_date = parse_date(args.end_date) if args.end_date else None

    dates = build_date_list(start_date, args.days, end_date)

    for target_date in dates:

        print(f"\nRunning {target_date}\n")

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
                    "coords": coords,
                }
            )

        date_str = target_date.strftime("%Y-%m-%d")

        build_map(events, date_str)

        # webbrowser.open(f"calendar_map/calendar_map_{date_str}.html")


if __name__ == "__main__":
    main()