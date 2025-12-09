import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from ai_model import decide_scenario, decide_scenario_v2

# Sadə yaddaşdaxili statistika
STATS = {
    "total_manual_decisions": 0,
    "total_ai_agreements": 0
}

# ==== FRONTEND QOVLUĞUNUN YOLU ====
# Bu fayl backend/app.py içindədir.
# Frontend isə ../frontend qovluğundadır.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# Flask tətbiqi: static_folder olaraq frontend qovluğunu göstəririk
app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,  # index.html, script.js, styles.css buradadır
    static_url_path=""           # fayllar birbaşa /index.html, /script.js kimi çıxacaq
)
CORS(app)  # Enable CORS for frontend requests


# ================== FRONTEND ROUTE ==================

@app.route("/")
def index():
    """
    Əsas səhifə: frontend/index.html faylını qaytarır.
    """
    return app.send_static_file("index.html")


# ================== API ENDPOINT-LƏRİ ==================

@app.route('/decide', methods=['POST'])
def decide():
    """
    Köhnə data modelinə əsasən qərar verən endpoint.
    """
    data = request.get_json()
    print("Gələn data:", data)

    if not data:
        return jsonify({"error": "JSON body boşdur və ya yanlışdır."}), 400

    result = decide_scenario(data)
    result["received"] = data
    return jsonify(result)


@app.route('/decide_v2', methods=['POST'])
def decide_v2():
    """
    Yeni data modelinə əsasən qərar verən endpoint.
    Burada track1 və track2 şəxs obyektlərinin listi kimi gəlir.
    """
    data = request.get_json()
    print("V2 ssenari gəldi:", data)

    if not data:
        return jsonify({"error": "JSON body boşdur və ya yanlışdır."}), 400

    result = decide_scenario_v2(data)
    result["received"] = data
    return jsonify(result)


@app.route('/compare', methods=['POST'])
def compare_decisions():
    """
    Eyni ssenarini bir neçə etik modda hesablayır və nəticələri müqayisə üçün qaytarır.
    Gözlənilən request formatı (minimum):
    {
      "track1": [ { "age": "...", "role": "...", "flags": [...] }, ... ],
      "track2": [ { "age": "...", "role": "...", "flags": [...] }, ... ],

      "deon_variant": "protect_children" (optional),
      "custom_rules": { ... } (optional),
      "include_ml": true/false (optional, default true),

      "manual_choice": 1 və ya 2 (optional – istifadəçinin öz qərarı)
    }
    """
    data = request.get_json() or {}

    track1 = data.get("track1", [])
    track2 = data.get("track2", [])

    deon_variant = data.get("deon_variant", "protect_children")
    custom_rules = data.get("custom_rules", {})
    include_ml = data.get("include_ml", True)

    manual_choice = data.get("manual_choice", None)

    results = {}

    # 1) Utilitarian
    util_scenario = {
        "track1": track1,
        "track2": track2,
        "mode": "utilitarian"
    }
    results["utilitarian"] = decide_scenario_v2(util_scenario)

    # 2) Deontological
    deon_scenario = {
        "track1": track1,
        "track2": track2,
        "mode": "deontological",
        "deon_variant": deon_variant
    }
    results["deontological"] = decide_scenario_v2(deon_scenario)

    # 3) Custom (əgər qaydalar verilibsə)
    if custom_rules:
        custom_scenario = {
            "track1": track1,
            "track2": track2,
            "mode": "custom",
            "custom_rules": custom_rules
        }
        results["custom"] = decide_scenario_v2(custom_scenario)

    # 4) ML v2
    if include_ml:
        ml_scenario = {
            "track1": track1,
            "track2": track2,
            "mode": "ml"
        }
        results["ml"] = decide_scenario_v2(ml_scenario)

    # 5) Manual seçimi statistikaya əlavə edək (əgər göndərilibsə)
    manual_info = {
        "manual_choice": manual_choice,
        "agreements": {}
    }

    if manual_choice in [1, 2]:
        STATS["total_manual_decisions"] += 1

        any_agree = False

        for mode_name, res in results.items():
            ai_choice = res.get("chosen_track")
            is_agree = (ai_choice == manual_choice)
            manual_info["agreements"][mode_name] = is_agree
            if is_agree:
                any_agree = True

        if any_agree:
            STATS["total_ai_agreements"] += 1

    # Ümumi uyğunluq faizi
    if STATS["total_manual_decisions"] > 0:
        agreement_rate = STATS["total_ai_agreements"] / STATS["total_manual_decisions"]
    else:
        agreement_rate = None

    return jsonify({
        "results": results,
        "manual": manual_info,
        "stats": {
            "total_manual_decisions": STATS["total_manual_decisions"],
            "total_ai_agreements": STATS["total_ai_agreements"],
            "agreement_rate": agreement_rate
        }
    })


if __name__ == '__main__':
    # Lokal işlətmək üçün
    app.run(debug=True, port=5000)
