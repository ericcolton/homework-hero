
import json
import os
from pathlib import Path

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def load_source_datasets():
    config_path = os.environ.get("HOMEWORK_HERO_CONFIG_PATH")
    if not config_path:
        raise RuntimeError("HOMEWORK_HERO_CONFIG_PATH is not set.")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to load HOMEWORK_HERO_CONFIG_PATH='{config_path}': {e}") from e

    reference_data_path = config.get("reference_data")
    if not reference_data_path:
        raise RuntimeError(
            f"Config at HOMEWORK_HERO_CONFIG_PATH='{config_path}' missing 'reference_data'."
        )

    source_datasets_path = Path(reference_data_path, "source_datasets.json")
    with open(source_datasets_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("Reference_Data/source_datasets.json must be a list or object.")
    data_sources = []
    for item in data:
        short_name = item.get("short_name")
        if not short_name:
            continue
        name = item.get("name") or short_name.replace("_", " ").title()
        data_sources.append({"id": short_name, "name": name})
    return data_sources

# --- CONFIGURATION / PLUGINS ---
app_config = {
    "data_sources": load_source_datasets(),
    "themes": [
        {
            "id": "kpop",
            "name": "KPop Demon Hunters",
            "css_class": "", # Default theme has no extra class
            "ui_title": "KPop Vocab Hunters",
            "ui_subtitle": "Hunt Vocabulary. Defeat Demons."
        },
        {
            "id": "wof",
            "name": "Wings of Fire",
            "css_class": "theme-wof",
            "ui_title": "Dragon Vocab Scrolls",
            "ui_subtitle": "Fly High. Burn Bright. Learn Words."
        }
    ],
    "models": [
        {"id": "gpt-5-mini", "name": "gpt-5-mini"},
        {"id": "gpt-4o", "name": "gpt-4o (High Cost)"},
    ],
    "sections": list(range(1, 16)), # Generates [1, 2, ... 15]
    "levels": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") # Generates ['A', 'B', ... 'Z']
}

@app.route('/')
def index():
    # Pass the config to the template to generate dropdowns dynamically
    return render_template('index.html', config=app_config)

@app.route('/generate', methods=['POST'])
def generate():
    # Placeholder for your generation logic
    data = request.form
    print(f"Generating with: {data}")
    return jsonify({"status": "success", "message": "Worksheet generation started..."})

@app.route('/about')
def about():
    return render_template('about.html', config=app_config)

if __name__ == '__main__':
    app.run(debug=True)
