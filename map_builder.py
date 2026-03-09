import folium
import json
import folium.utilities
import openrouteservice
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY= os.getenv("ORS_API_KEY")

import math

def calculate_bearing(start, end):
    """
    Calculate bearing in degrees from start to end.
    start/end: [lat, lon]
    Returns angle in degrees clockwise from north.
    """
    lat1 = math.radians(start[0])
    lat2 = math.radians(end[0])
    diffLong = math.radians(end[1] - start[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - \
        math.sin(lat1) * math.cos(lat2) * math.cos(diffLong)

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def save_metadata(date, events):
    stops = []
    for e in events:
        stops.append({
            "summary": e["summary"],
            "time": e["time"],
            "lat": e["coords"][0],
            "lon": e["coords"][1]
        })
    data = {
        "date": date,
        "num_stops": len(stops),
        "stops": stops
    }
    with open(f"calendar_maps/{date}.json", "w") as f:
        json.dump(data, f, indent=2)

def build_map(events, date_str):
    if not events:
        print("No events with locations.")
        return

    # ORS expects coordinates as [lon, lat]
    coords_ors = [[e["coords"][1], e["coords"][0]] for e in events]

    client = openrouteservice.Client(key=API_KEY)

    # Get a real road route from ORS
    route_data = client.directions(
        coordinates=coords_ors,
        profile="foot-walking",
        format="geojson",
        optimize_waypoints=False
    )

    # Extract route coordinates from GeoJSON (no decode_polyline needed)
    route_coords = route_data["features"][0]["geometry"]["coordinates"]
    # Convert to [lat, lon] for Folium
    route_latlngs = [[c[1], c[0]] for c in route_coords]

    # Center the map
    center = [
        sum(c[0] for c in route_latlngs) / len(route_latlngs),
        sum(c[1] for c in route_latlngs) / len(route_latlngs)
    ]

    m = folium.Map(location=center, zoom_start=12)

    # Draw the main route
    route_line = folium.PolyLine(
        route_latlngs,
        color="#1f78b4",
        weight=5,
        opacity=0.8
    ).add_to(m)

    # # Add directional arrows along the route
    # step = max(1, len(route_latlngs)//100)
    # for i in range(0, len(route_latlngs), step):
    #     if i + 1 < len(route_latlngs):
    #         start = route_latlngs[i]
    #         end = route_latlngs[i + 1]
    #         folium.RegularPolygonMarker(
    #             location=start,
    #             number_of_sides=3,
    #             radius=6,
    #             fill_opacity=0.9,
    #             rotation=calculate_bearing(start, end)
    #         ).add_to(m)

    # Track duplicates for repeated location circles
    seen = {}
    for i, e in enumerate(events, start=1):
        lat, lon = e["coords"]
        coord_tuple = (lat, lon)
        popup = f"""
        <div style="width:220px;font-family:sans-serif">
            <b>Stop {i}</b><br>
            <b>{e['summary']}</b><br>
            🕒 {e['time']}
        </div>
        """
        marker_color = "#2563eb"
        if i == 1:
            marker_color = "#16a34a"
        elif i == len(events):
            marker_color = "#dc2626"

        folium.Marker(
            [lat, lon],
            popup=popup,
            tooltip=e['summary'],
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    background:{marker_color};
                    color:white;
                    border-radius:50%;
                    width:30px;
                    height:30px;
                    text-align:center;
                    font-weight:bold;
                    line-height:30px;
                    box-shadow:0 3px 8px rgba(0,0,0,0.35);
                ">
                {i}
                </div>
                """
            )
        ).add_to(m)

        if coord_tuple in seen:
            # repeated location
            folium.CircleMarker(
                [lat, lon],
                radius=6,
                color="orange",
                fill=True,
                fill_opacity=0.9
            ).add_to(m)
            # optional loop hint line
            start = [events[seen[coord_tuple]]["coords"][0], events[seen[coord_tuple]]["coords"][1]]
            folium.PolyLine(
                [start, [lat, lon]],
                color="purple",
                weight=2,
                dash_array="3,6"
            ).add_to(m)
        else:
            seen[coord_tuple] = i-1

    # Sidebar itinerary
    sidebar_items = ""
    for i, e in enumerate(events, start=1):
        sidebar_items += f"""
        <div style="margin-bottom:12px">
            <b>{i}. {e['time']}</b><br>
            {e['summary']}
        </div>
        """
    sidebar = f"""
        <div id="sidebar" style="
        position: fixed;
        top: 10px;
        left: 10px;
        width: 260px;
        max-height: 90%;
        overflow:auto;
        background:white;
        padding:18px;
        border-radius:10px;
        box-shadow:0 6px 16px rgba(0,0,0,0.25);
        z-index:9999;
        font-family:sans-serif;
        ">
        <h3 style="margin-top:0">Today's Route</h3>
        {sidebar_items}
        </div>

        <script>
        if (window !== window.parent) {{
            document.getElementById("sidebar").style.display = "none";
        }}
        </script>
    """
    m.get_root().html.add_child(folium.Element(sidebar))

    m.save(f"calendar_maps/{date_str}.html")
    save_metadata(date_str, events)