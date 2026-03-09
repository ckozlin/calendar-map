import folium
import json

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

    lats = [e["coords"][0] for e in events]
    lons = [e["coords"][1] for e in events]

    center = [sum(lats) / len(lats), sum(lons) / len(lons)]

    m = folium.Map(location=center, zoom_start=12)

    coords = []

    for i, e in enumerate(events, start=1):
        lat, lon = e["coords"]

        popup = f"""
        <div style="width:200px">
            <b>Stop {i}</b><br>
            <b>{e['summary']}</b><br>
            🕒 {e['time']}
        </div>
        """

        folium.Marker(
            [lat, lon],
            popup=popup,
            tooltip=popup,
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    background:#2563eb;
                    color:white;
                    border-radius:50%;
                    width:28px;
                    height:28px;
                    text-align:center;
                    font-weight:bold;
                    line-height:28px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.4);
                ">
                {i}
                </div>
                """
            )
        ).add_to(m)

        coords.append([lat, lon])

    if len(coords) > 1:
        folium.PolyLine(
            coords,
            color="blue",
            weight=3.5,
            dash_array="8,8"
        ).add_to(m)

    m.fit_bounds(coords)

    sidebar_items = ""

    for i, e in enumerate(events, start=1):
        sidebar_items += f"""
        <div style="margin-bottom:10px">
            <b>{i}. {e['time']}</b><br>
            {e['summary']}
        </div>
        """

    sidebar = f"""
        <div id="sidebar" style="
        position: fixed;
        top: 10px;
        left: 10px;
        width: 250px;
        max-height: 90%;
        overflow:auto;
        background:white;
        padding:15px;
        border-radius:8px;
        box-shadow:0 4px 12px rgba(0,0,0,0.2);
        z-index:9999;
        font-family:sans-serif;
        ">
        <h3>Today's Route</h3>
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