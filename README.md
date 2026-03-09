# Calendar Route Maps

This project converts calendar events with locations into interactive daily maps.

The maps show:

• Ordered stops  
• Travel route between events  
• Directional arrows  
• Repeated locations  
• Start and end markers  
• Sidebar itinerary

The output is an interactive HTML map for each day.

---

## Example Output

Each day generates:

calendar_maps/
2026-02-14.html
2026-02-14.json

The HTML contains the interactive map.

The JSON contains structured metadata.

---

## Features

Directional route arrows  
Visual numbered stops  
Start and end highlights  
Repeated location detection  
Loop-back visualization  
Sidebar itinerary panel

---

## Map Legend

Green marker = start  
Red marker = final stop  
Blue markers = normal stops  
Orange circle = repeated location

Blue line = route

---

## Usage

```
python daymap.py --date <YYYY-MM-DD> --calendar <calendar> @group.calendar.google.com --timezone <pytz timezone>
```
