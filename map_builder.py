import folium
import json
import openrouteservice
from dotenv import load_dotenv
import os
import math

load_dotenv()
API_KEY = os.getenv("ORS_API_KEY")


def haversine(a, b):
    R = 6371
    lat1, lon1 = a
    lat2, lon2 = b

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    x = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(x), math.sqrt(1 - x))


def save_metadata(date, events):
    stops = []
    for e in events:
        stops.append(
            {
                "summary": e["summary"],
                "time": e["time"],
                "lat": e["coords"][0],
                "lon": e["coords"][1],
            }
        )

    data = {"date": date, "num_stops": len(stops), "stops": stops}

    with open(f"calendar_maps/{date}.json", "w") as f:
        json.dump(data, f, indent=2)


def build_map(events, date_str):

    if not events:
        print("No events with locations.")
        return

    client = openrouteservice.Client(key=API_KEY)

    # ---------------------------------------------------
    # Build legs by routing each pair of stops
    # ---------------------------------------------------

    leg_routes = []
    leg_distances = []

    for i in range(len(events) - 1):
        a = events[i]["coords"]
        b = events[i + 1]["coords"]

        leg = client.directions(
            coordinates=[[a[1], a[0]], [b[1], b[0]]],
            profile="foot-walking",
            format="geojson",
        )

        coords = leg["features"][0]["geometry"]["coordinates"]
        coords = [[c[1], c[0]] for c in coords]
        leg_routes.append(coords)

        # Safely extract distance
        segments = leg["features"][0]["properties"].get("segments", [])
        if segments and "distance" in segments[0]:
            d = segments[0]["distance"] / 1000
        else:
            # fallback if not present
            d = sum(haversine(coords[j], coords[j+1]) for j in range(len(coords)-1))
        leg_distances.append(d)

    # Flatten route for drawing
    route_latlngs = []
    for leg in leg_routes:
        route_latlngs.extend(leg)

    # ---------------------------------------------------
    # Map setup
    # ---------------------------------------------------

    center = [
        sum(c[0] for c in route_latlngs) / len(route_latlngs),
        sum(c[1] for c in route_latlngs) / len(route_latlngs),
    ]

    m = folium.Map(location=center)
    m.fit_bounds(route_latlngs)

    folium.PolyLine(route_latlngs, color="#1f78b4", weight=5, opacity=0.8).add_to(m)

    # ---------------------------------------------------
    # Stop markers
    # ---------------------------------------------------

    seen = {}

    for i, e in enumerate(events, start=1):

        lat, lon = e["coords"]

        key = (round(lat, 6), round(lon, 6))
        count = seen.get(key, 0)
        seen[key] = count + 1

        if count > 0:
            angle = count * 45
            offset = 0.00015
            lat += offset * math.cos(math.radians(angle))
            lon += offset * math.sin(math.radians(angle))

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
            tooltip=e["summary"],
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
            ),
        ).add_to(m)

    # ---------------------------------------------------
    # Sidebar itinerary
    # ---------------------------------------------------

    sidebar_items = ""

    for i, e in enumerate(events):

        line = f"<b>{i+1}. {e['time']}</b><br>{e['summary']}"

        if i < len(leg_distances):
            line += f"<br><span style='color:#666'>Walk {leg_distances[i]:.2f} km</span>"

        sidebar_items += f"<div style='margin-bottom:12px'>{line}</div>"

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

    <style>
    /* Hide sidebar on screens narrower than 768px */
    @media (max-width: 768px) {{
        #sidebar {{
            display: none !important;
        }}
    }}
    </style>

    <script>
    if (window !== window.parent) {{
        document.getElementById("sidebar").style.display = "none";
    }}
    </script>
    """

    m.get_root().html.add_child(folium.Element(sidebar))

    # ---------------------------------------------------
    # Animation
    # ---------------------------------------------------

    legs_js = json.dumps(leg_routes)

    total_km = sum(leg_distances)
    duration_seconds = min(40, max(20, total_km * 1.2))
    total_points = sum(len(l) for l in leg_routes)
    frame_delay = max(8, int((duration_seconds * 1000) / total_points))

    animation_script = f"""
<script>

window.addEventListener("load", function() {{

    var map = {m.get_name()};
    var legs = {legs_js};

    var marker = L.circleMarker(legs[0][0], {{
        radius:8,
        color:"#6b21a8",
        fillColor:"#9333ea",
        fillOpacity:1,
        weight:3
    }}).addTo(map);

    var trail = L.polyline([], {{
        color:"#a855f7",
        weight:4,
        opacity:0.6
    }}).addTo(map);

    function pulseStop(pt) {{

        var circle = L.circle(pt,{{
            radius:40,
            color:"#9333ea",
            opacity:0.6,
            weight:2,
            fill:false
        }}).addTo(map);

        var r = 40;

        var grow = setInterval(function(){{
            r += 20;
            circle.setRadius(r);
            circle.setStyle({{opacity:0.6-(r/300)}});

            if(r>220){{
                map.removeLayer(circle);
                clearInterval(grow);
            }}

        }},40);
    }}

    var legIndex = 0;
    var pointIndex = 0;
    var trailCoords = [];

    function step(){{

        var leg = legs[legIndex];
        var pt = leg[pointIndex];

        marker.setLatLng(pt);

        trailCoords.push(pt);
        trail.setLatLngs(trailCoords);

        pointIndex++;

        if(pointIndex >= leg.length){{

            pulseStop(pt);

            legIndex++;

            if(legIndex >= legs.length){{
                legIndex = 0;
                pointIndex = 0;
                trailCoords = [];
                trail.setLatLngs([]);
                setTimeout(step,1200);
                return;
            }}

            pointIndex = 0;
            setTimeout(step,900);
            return;
        }}

        setTimeout(step,{frame_delay});
    }}

    step();

}});
</script>
"""

    m.get_root().html.add_child(folium.Element(animation_script))

    # ---------------------------------------------------

    m.save(f"calendar_maps/{date_str}.html")
    save_metadata(date_str, events)