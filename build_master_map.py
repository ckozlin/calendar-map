import json
import os
import folium

MAP_DIR = "calendar_maps"

files = [f for f in os.listdir(MAP_DIR) if f.endswith(".json")]

all_points = []

for file in files:

    with open(f"{MAP_DIR}/{file}") as f:
        data = json.load(f)

    for stop in data["stops"]:
        stop["date"] = data["date"]
        all_points.append(stop)

if not all_points:
    exit()

center = [
    sum(p["lat"] for p in all_points) / len(all_points),
    sum(p["lon"] for p in all_points) / len(all_points)
]

m = folium.Map(location=center, zoom_start=6)

for p in all_points:

    popup = f"""
    <b>{p['summary']}</b><br>
    {p['date']} {p['time']}
    """

    folium.Marker(
        [p["lat"], p["lon"]],
        popup=popup
    ).add_to(m)

m.save(f"{MAP_DIR}/master_map.html")