import folium
import json
import folium.utilities
import openrouteservice
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY= os.getenv("ORS_API_KEY")

import math

def haversine(a, b):
    R = 6371
    lat1, lon1 = a
    lat2, lon2 = b

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)

    x = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)

    return 2 * R * math.atan2(math.sqrt(x), math.sqrt(1-x))


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

    coords_ors = [[e["coords"][1], e["coords"][0]] for e in events]

    client = openrouteservice.Client(key=API_KEY)

    route_data = client.directions(
        coordinates=coords_ors,
        profile="foot-walking",
        format="geojson",
        optimize_waypoints=False
    )

    route_coords = route_data["features"][0]["geometry"]["coordinates"]

    route_latlngs = [[c[1], c[0]] for c in route_coords]

    center = [
        sum(c[0] for c in route_latlngs) / len(route_latlngs),
        sum(c[1] for c in route_latlngs) / len(route_latlngs)
    ]

    m = folium.Map(location=center)

    m.fit_bounds(route_latlngs)

    folium.PolyLine(
        route_latlngs,
        color="#1f78b4",
        weight=5,
        opacity=0.8
    ).add_to(m)

    # ---------------------------------------------------
    # MOVING DOT ANIMATION (POLISHED)
    # ---------------------------------------------------

    route_js = json.dumps(route_latlngs)
    stops_js = json.dumps([e["coords"] for e in events])
    map_var = m.get_name()

    total_km = 0
    for i in range(len(route_latlngs)-1):
        total_km += haversine(route_latlngs[i], route_latlngs[i+1])

    duration_seconds = max(10, total_km * 4)
    frame_delay = int((duration_seconds * 1000) / len(route_latlngs))

    animation_script = f"""
    <script>

    window.addEventListener("load", function() {{

        var map = {map_var};

        var route = {route_js};
        var stops = {stops_js};

        // glowing purple marker
        var marker = L.circleMarker(route[0], {{
            radius:8,
            color:"#6b21a8",
            fillColor:"#9333ea",
            fillOpacity:1,
            weight:3
        }}).addTo(map);

        // trail behind marker
        var trail = L.polyline([], {{
            color:"#a855f7",
            weight:4,
            opacity:0.6
        }}).addTo(map);

        function dist(a,b){{
            var dx = a[0]-b[0];
            var dy = a[1]-b[1];
            return dx*dx + dy*dy;
        }}

        var stopIndices = [];

        stops.forEach(function(stop){{
            var bestIndex = 0;
            var bestDist = Infinity;

            for(var i=0;i<route.length;i++){{
                var d = dist(route[i], stop);
                if(d < bestDist){{
                    bestDist = d;
                    bestIndex = i;
                }}
            }}

            stopIndices.push(bestIndex);
        }});

        var i = 0;
        var trailCoords = [];

        function moveMarker(){{

            var pt = route[i];

            marker.setLatLng(pt);

            trailCoords.push(pt);
            trail.setLatLngs(trailCoords);

            if(stopIndices.includes(i)){{
                setTimeout(step, 900);
            }} else {{
                setTimeout(step, {frame_delay});
            }}

        }}

        function step(){{

            i++;

            if(i >= route.length){{
                i = 0;
                trailCoords = [];
                trail.setLatLngs([]);
            }}

            moveMarker();
        }}

        moveMarker();

    }});

    </script>
    """

    m.get_root().html.add_child(folium.Element(animation_script))

    # ---------------------------------------------------
    # EVENT MARKERS
    # ---------------------------------------------------

    seen = {}

    for i, e in enumerate(events, start=1):

        lat, lon = e["coords"]

        key = (round(lat,6), round(lon,6))
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

    # ---------------------------------------------------
    # SIDEBAR WITH DISTANCES
    # ---------------------------------------------------

    sidebar_items = ""

    for i, e in enumerate(events, start=1):

        distance_html = ""

        if i < len(events):
            dist = haversine(events[i-1]["coords"], events[i]["coords"])
            distance_html = f"<div style='font-size:12px;color:#6b7280'>↳ {round(dist,1)} km</div>"

        sidebar_items += f"""
        <div style="margin-bottom:12px">
            <b>{i}. {e['time']}</b><br>
            {e['summary']}
            {distance_html}
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