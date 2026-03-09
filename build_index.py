import os
import json

MAP_DIR = "calendar_maps"

files = sorted(
    f for f in os.listdir(MAP_DIR)
    if f.endswith(".json")
)

cards = ""
options = ""

for file in files:

    with open(f"{MAP_DIR}/{file}") as f:
        data = json.load(f)

    date = data["date"]
    stops = data["num_stops"]

    preview = "<br>".join(
        s["summary"] for s in data["stops"][:3]
    )

    cards += f"""
    <div class="card">
        <h3>{date}</h3>
        <p>{stops} stops</p>
        <p>{preview}</p>
        <a href="{date}.html">Open Map →</a>
        <iframe src="{date}.html"
        width="100%"
        height="150"
        style="border:none;">
</iframe>
    </div>
    """

    options += f'<option value="{date}.html">{date}</option>'

html = f"""
<!DOCTYPE html>
<html>
<head>

<h2>Trip Overview</h2>

<iframe src="master_map.html"
        width="100%"
        height="400"
        style="border:none; border-radius:10px;">
</iframe>
<title>Trip Maps</title>

<style>

body {{
    font-family: system-ui;
    max-width: 900px;
    margin: 40px auto;
}}

h1 {{
    margin-bottom: 30px;
}}

select {{
    font-size: 16px;
    padding: 8px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill,minmax(220px,1fr));
    gap: 20px;
    margin-top: 30px;
}}

.card {{
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 10px;
}}

.card a {{
    text-decoration: none;
    font-weight: bold;
}}

</style>

<script>

function goToDate() {{
    const select = document.getElementById("dateSelect");
    window.location = select.value;
}}

</script>

</head>

<body>

<h1>Trip Maps</h1>

<label>Select day:</label>

<select id="dateSelect" onchange="goToDate()">
<option value="">Choose...</option>
{options}
</select>

<div class="grid">
{cards}
</div>

</body>
</html>
"""

with open(f"{MAP_DIR}/index.html", "w") as f:
    f.write(html)