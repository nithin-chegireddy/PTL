import pandas as pd
import time
import json
import requests
import os
from flask import Flask, jsonify

# ============================================================
# FIXED OUTPUT JSON DIRECTORY
# ============================================================
DATA_DIR = r"data"
os.makedirs(DATA_DIR, exist_ok=True)

# Output
OML_JSON = os.path.join(DATA_DIR, "oml_output.json")

# ============================================================
# INPUT EXCEL
# ============================================================
INPUT_EXCEL = os.path.join(DATA_DIR, "COMBINED_INPUTS.xlsx")
df = pd.read_excel(INPUT_EXCEL)

oml_list = df.iloc[:, 2].dropna().astype(str).tolist()

# ============================================================
# OML API (no changes)
# ============================================================
def fetch_oml(cn):
    url = f"https://omsl.omlogistics.co.in/oracle/android_api/cn_enquiry.php?cn_no={cn}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()

        data = r.json()
        if "cn_enquiry" not in data or len(data["cn_enquiry"]) == 0:
            return None, None

        item = data["cn_enquiry"][0]

        return item.get("EXPECTED_DELIVERY_DATE", ""), item.get("STATUS", "")
    except:
        return None, None


def run_oml(oml_list):
    print("\n===== RUNNING OML TRACKING =====")

    results = []

    for cn in oml_list:
        exp, status = fetch_oml(cn)

        results.append({
            "CN_NO": cn,
            "EXPECTED_DELIVERY_DATE": exp,
            "STATUS": status
        })

    with open(OML_JSON, "w") as f:
        json.dump(results, f, indent=4)

    print("✅ OML JSON SAVED:", OML_JSON)


# ============================================================
# FLASK API
# ============================================================
app = Flask(__name__)

@app.route("/run_oml")
def api_run_oml():
    run_oml(oml_list)
    return jsonify({"status": "success", "message": "OML scraping completed"})


@app.route("/get_oml")
def get_oml_json():
    if os.path.exists(OML_JSON):
        with open(OML_JSON, "r") as f:
            return jsonify(json.load(f))
    return jsonify([])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
