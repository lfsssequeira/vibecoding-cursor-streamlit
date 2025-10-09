#!/usr/bin/env python3
from flask import Flask, jsonify, render_template_string
import requests

app = Flask(__name__)

# Nazaré coordinates (Praia do Norte area)
NAZARE_LAT = 39.605
NAZARE_LON = -9.085
OPEN_METEO_URL = (
	"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&hourly=wave_height&timezone=auto"
)

PAGE = """
<!doctype html>
<title>Nazaré Wave Height</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
	body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; }
	.card { max-width: 520px; padding: 1.5rem; border-radius: 12px; background: #0b1020; color: #eaf1ff; }
	.big { font-size: 2.5rem; font-weight: 700; }
	.dim { color: #9fb3d1; margin-top: .5rem; }
	.error { color: #ff6b6b; }
	footer { margin-top: 1rem; color: #6b7a90; font-size: .9rem; }
	button { margin-top: 1rem; padding: .5rem 1rem; border-radius: 8px; border: 0; background: #2a62ff; color: white; cursor: pointer; }
</style>
<div class="card">
	<div class="big">{{ wave_text }}</div>
	<div class="dim">Location: Nazaré, PT • Data source: Open‑Meteo (hourly wave height)</div>
	<button onclick="window.location.reload()">Refresh</button>
</div>
<footer>Units: meters (m). Times are local to your timezone.</footer>
"""


def fetch_wave_height():
	url = OPEN_METEO_URL.format(lat=NAZARE_LAT, lon=NAZARE_LON)
	r = requests.get(url, timeout=10)
	r.raise_for_status()
	data = r.json()
	hourly = data.get("hourly", {})
	heights = hourly.get("wave_height") or []
	times = hourly.get("time") or []
	if not heights or not times:
		return None, None
	# Use the first hour as "current" approximation
	return heights[0], times[0]


@app.route("/")
def home():
	try:
		height, when = fetch_wave_height()
		if height is None:
			return render_template_string(PAGE, wave_text="Wave height: unavailable"), 200
		return render_template_string(PAGE, wave_text=f"Wave height: {height:.2f} m")
	except Exception as exc:
		return render_template_string(PAGE, wave_text=f"Error: {exc}"), 200


@app.route("/api")
def api():
	try:
		height, when = fetch_wave_height()
		return jsonify({"height_m": height, "time": when})
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
