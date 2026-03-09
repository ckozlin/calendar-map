import folium


def build_map(events):
    m = folium.Map(location=[39.5, -98.35], zoom_start=4)

    coords = []

    for e in events:
        if "coords" not in e:
            continue

        lat, lon = e["coords"]

        folium.Marker(
            [lat, lon],
            popup=e["summary"]
        ).add_to(m)

        coords.append([lat, lon])

    if len(coords) > 1:
        folium.PolyLine(coords).add_to(m)

    m.save("calendar_map.html")