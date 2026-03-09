import os

MAP_DIR = "calendar_map"

files = sorted(
    f for f in os.listdir(MAP_DIR)
    if f.endswith(".html") and f != "index.html"
)

links = ""

for f in files:
    date = f.replace(".html", "")
    links += f'<li><a href="{f}">{date}</a></li>\n'

html = f"""
<html>
<head>
<title>Maps</title>
<style>
body {{
    font-family: sans-serif;
    max-width: 700px;
    margin: 40px auto;
}}
li {{
    margin: 10px 0;
}}
a {{
    font-size: 18px;
}}
</style>
</head>

<body>
<h1>Trip Maps</h1>

<ul>
{links}
</ul>

</body>
</html>
"""

with open(f"{MAP_DIR}/index.html", "w") as f:
    f.write(html)