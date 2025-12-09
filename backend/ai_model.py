import os
import joblib
import numpy as np
# Qlobal dəyişən – model bir dəfə yüklənsin
_ml_model = None

def load_ml_model():
    global _ml_model
    if _ml_model is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "trolley_model_v2.pkl")
        if not os.path.exists(model_path):
            print("Xəbərdarlıq: trolley_model_v2.pkl tapılmadı. Əvvəlcə train_model_v2.py-ni işə salın.")
            return None
        _ml_model = joblib.load(model_path)
        print("ML v2 modeli yükləndi.")
    return _ml_model



def decide_ml(scenario: dict) -> dict:
    """
    Verilən ssenariyə əsasən ML modeli ilə qərar verir.
    """
    model = load_ml_model()
    if model is None:
        # Model yoxdursa, fallback kimi default qayda
        return {
            "chosen_track": 1,
            "reason": "ML modeli tapılmadı, default olaraq Track 1 seçildi.",
            "track1_total": None,
            "track2_total": None
        }

    track1 = scenario.get("track1", {})
    track2 = scenario.get("track2", {})

    t1_children = track1.get("children", 0)
    t1_adults = track1.get("adults", 0)
    t1_elders = track1.get("elders", 0)

    t2_children = track2.get("children", 0)
    t2_adults = track2.get("adults", 0)
    t2_elders = track2.get("elders", 0)

    # Modelin gözlədiyi feature düzülüşü:
    features = np.array([[ 
        t1_children, t1_adults, t1_elders,
        t2_children, t2_adults, t2_elders
    ]])

    pred = model.predict(features)[0]  # 1 və ya 2

    track1_total = t1_children + t1_adults + t1_elders
    track2_total = t2_children + t2_adults + t2_elders

    reason = (
        f"Qərar ML modeli tərəfindən verildi. Model sənin əvvəlcədən etiketlədiyin "
        f"ssenarilərə əsaslanaraq Track {pred} seçdi."
    )

    return {
        "chosen_track": int(pred),
        "reason": reason,
        "track1_total": track1_total,
        "track2_total": track2_total
    }


def aggregate_track_for_ml(track: list) -> dict:
    """
    Yeni data modelindəki track-i (şəxslər listi) ML modelinin başa düşdüyü
    sadə formata çevirir:
    {
        "children": X,
        "adults": Y,
        "elders": Z
    }

    Burada:
    - age == "child"  → children
    - age == "teen" / "young" / "adult" → adults
    - age == "elder" → elders
    Digər age dəyərləri üçün ehtiyatla adults kimi saya bilərik.
    """
    children = 0
    adults = 0
    elders = 0

    for person in track:
        age = person.get("age")
        if age == "child":
            children += 1
        elif age in ("teen", "young", "adult", None):
            adults += 1
        elif age == "elder":
            elders += 1
        else:
            # Naməlum age üçün default olaraq böyüklərə əlavə edirik
            adults += 1

    return {
        "children": children,
        "adults": adults,
        "elders": elders
    }

ML_V2_HEADER = [
    "t1_child", "t1_teen", "t1_adult", "t1_elder",
    "t1_doctor", "t1_nurse", "t1_teacher", "t1_engineer",
    "t1_student", "t1_unemployed", "t1_retired",
    "t1_pregnant_role", "t1_criminal", "t1_thief", "t1_other",
    "t1_pregnant_flag", "t1_disabled_flag", "t1_innocent_flag",
    "t1_guilty_flag", "t1_law_breaker_flag", "t1_relative_flag",
    "t1_friend_flag", "t1_stranger_flag", "t1_saves_lives_flag",
    "t1_vulnerable_flag",

    "t2_child", "t2_teen", "t2_adult", "t2_elder",
    "t2_doctor", "t2_nurse", "t2_teacher", "t2_engineer",
    "t2_student", "t2_unemployed", "t2_retired",
    "t2_pregnant_role", "t2_criminal", "t2_thief", "t2_other",
    "t2_pregnant_flag", "t2_disabled_flag", "t2_innocent_flag",
    "t2_guilty_flag", "t2_law_breaker_flag", "t2_relative_flag",
    "t2_friend_flag", "t2_stranger_flag", "t2_saves_lives_flag",
    "t2_vulnerable_flag",
]


def track_to_features_v2(prefix: str, persons: list[dict]) -> dict:
    """
    Yeni data modelindəki şəxslər siyahısını ML v2 üçün feature-lərə çevirir.
    prefix: 't1_' və ya 't2_'
    """
    # Məsələn, prefix='t1_' olanda yalnız t1_ ilə başlayan sütunlara 0 yazırıq
    feat = {col: 0 for col in ML_V2_HEADER if col.startswith(prefix)}

    for p in persons:
        age = p.get("age")
        role = p.get("role")
        flags = p.get("flags", [])

        # Yaş
        if age in ["child", "teen", "adult", "elder"]:
            feat[f"{prefix}{age}"] += 1
        else:
            feat[f"{prefix}adult"] += 1

        # Rol
        role_key = role if role is not None else "other"
        if role_key not in [
            "doctor", "nurse", "teacher", "engineer",
            "student", "unemployed", "retired",
            "pregnant_role", "criminal", "thief", "other"
        ]:
            role_key = "other"

        feat[f"{prefix}{role_key}"] += 1

        # Flag-lar
        for f in flags:
            col_name = f"{prefix}{f}_flag"
            if col_name in feat:
                feat[col_name] += 1

    return feat


def decide_ml_v2(track1: list[dict], track2: list[dict]) -> dict:
    """
    Yeni ML v2 modeli ilə qərar verir.
    track1 və track2 – yeni strukturda şəxslər siyahısıdır.
    """
    model = load_ml_model()
    if model is None:
        return {
            "chosen_track": 1,
            "reason": "ML v2 modeli tapılmadı, default olaraq Track 1 seçildi."
        }

    feat_t1 = track_to_features_v2("t1_", track1)
    feat_t2 = track_to_features_v2("t2_", track2)

    # ML_V2_HEADER sırasına uyğun olaraq vektoru yığırıq
    vector = []
    for col in ML_V2_HEADER:
        if col.startswith("t1_"):
            vector.append(feat_t1.get(col, 0))
        else:
            vector.append(feat_t2.get(col, 0))

    vector = np.array([vector])  # shape: (1, n_features)

    pred = int(model.predict(vector)[0])

    reason = "Ssenari yaş, rol və atributlar əsasında ML v2 modeli ilə qiymətləndirildi."

    return {
        "chosen_track": pred,
        "reason": reason
    }

def decide_scenario(scenario: dict) -> dict:
    """
    Ssenariyə və seçilmiş etik rejimə əsasən qərar verən funksiya.
    scenario = {
        "track1": {...},
        "track2": {...},
        "mode": "normal" / "children_first" / "ml"
    }
    """

    # MODE oxunur (default olaraq NORMAL)
    mode = scenario.get("mode", "normal")

    # Əgər ML seçilibsə → birbaşa ML qərarı qaytar
    if mode == "ml":
        return decide_ml(scenario)

    # Track məlumatlarını oxuyaq
    track1 = scenario.get("track1", {})
    track2 = scenario.get("track2", {})

    t1_children = track1.get("children", 0)
    t1_adults = track1.get("adults", 0)
    t1_elders = track1.get("elders", 0)

    t2_children = track2.get("children", 0)
    t2_adults = track2.get("adults", 0)
    t2_elders = track2.get("elders", 0)

    track1_total = t1_children + t1_adults + t1_elders
    track2_total = t2_children + t2_adults + t2_elders

    # ===============================
    # MODE 1 — NORMAL (ən az itki)
    # ===============================
    if mode == "normal":

        if track1_total < track2_total:
            chosen_track = 1
            reason = (
                f"Track 1 seçildi, çünki orada {track1_total} nəfər, "
                f"Track 2-də isə {track2_total} nəfər var."
            )

        elif track2_total < track1_total:
            chosen_track = 2
            reason = (
                f"Track 2 seçildi, çünki orada {track2_total} nəfər, "
                f"Track 1-də isə {track1_total} nəfər var."
            )

        else:
            # Say bərabərdir → uşaqlara baxırıq
            if t1_children > t2_children:
                chosen_track = 2
                reason = (
                    "Say bərabərdir, amma Track 1-də daha çox uşaq var. "
                    "Ona görə Track 2 qurban verildi."
                )
            elif t2_children > t1_children:
                chosen_track = 1
                reason = (
                    "Say bərabərdir, amma Track 2-də daha çox uşaq var. "
                    "Ona görə Track 1 qurban verildi."
                )
            else:
                chosen_track = 1
                reason = (
                    "Hər iki tərəf eynidir. Default olaraq Track 1 seçildi."
                )

    # ===============================================
    # MODE 2 — CHILDREN FIRST (uşaqlar prioritet)
    # ===============================================
    elif mode == "children_first":

        # Uşaqları maksimum qorumağa çalışırıq
        if t1_children < t2_children:
            chosen_track = 1
            reason = (
                "Uşaqlar prioritet rejimində: Track 1-də daha az uşaq var. "
                "Ona görə Track 1 qurban verildi, daha çox uşaq xilas olur."
            )
        elif t2_children < t1_children:
            chosen_track = 2
            reason = (
                "Uşaqlar prioritet rejimində: Track 2-də daha az uşaq var. "
                "Ona görə Track 2 qurban verildi."
            )
        else:
            # Uşaqlar bərabərdirsə → ümumi itkiyə bax
            if track1_total < track2_total:
                chosen_track = 1
                reason = (
                    "Uşaqlar bərabərdir, ona görə ümumi itki az olan Track 1 seçildi."
                )
            elif track2_total < track1_total:
                chosen_track = 2
                reason = (
                    "Uşaqlar bərabərdir, ona görə ümumi itki az olan Track 2 seçildi."
                )
            else:
                chosen_track = 1
                reason = (
                    "Hər şey bərabərdir. Default olaraq Track 1 seçildi."
                )

    # MODE tanınmadıqda — fallback
    else:
        chosen_track = 1
        reason = "Naməlum etik rejim. Default olaraq Track 1 seçildi."

    return {
        "chosen_track": chosen_track,
        "reason": reason,
        "track1_total": track1_total,
        "track2_total": track2_total
    }

# ====== Utilitarian mod üçün default ağırlıq cədvəlləri ======

AGE_WEIGHTS = {
    "child": 4,      # uşaqlar – ən yüksək prioritet
    "teen": 3,
    "young": 3,
    "adult": 2,
    "elder": 1
}

ROLE_WEIGHTS = {
    "doctor": 4,
    "nurse": 3,
    "teacher": 3,
    "engineer": 2,
    "student": 2,
    "unemployed": 1,
    "retired": 1,
    "pregnant": 3,   # əgər rolu bu cür saxlasan
    "criminal": -1,
    "thief": 0,
    "other": 1
}

FLAG_WEIGHTS = {
    "pregnant": 3,      # hamiləlik atribut kimi gələndə
    "disabled": 2,
    "innocent": 1,
    "guilty": -2,
    "law_breaker": -1,
    "relative": 2,
    "friend": 1,
    "stranger": 0,
    "saves_lives": 2,
    "vulnerable": 2
}

def _get_age_weight(age: str) -> int:
    if age is None:
        return 1
    return AGE_WEIGHTS.get(age, 1)


def _get_role_weight(role: str) -> int:
    if role is None:
        return 1
    return ROLE_WEIGHTS.get(role, 1)


def _get_flags_weight(flags) -> int:
    if not flags:
        return 0
    total = 0
    for f in flags:
        total += FLAG_WEIGHTS.get(f, 0)
    return total

def merge_weights(defaults: dict, custom: dict | None) -> dict:
    """
    Default ağırlıqları istifadəçi tərəfindən verilən custom dəyərlərlə birləşdirir.
    Custom eyni açarı ehtiva edərsə, default-u override edir.
    """
    merged = defaults.copy()
    if custom:
        merged.update(custom)
    return merged


def compute_person_value(person: dict) -> int:
    """
    Bir şəxsin etik dəyərini hesablayır:
    yaş + rol + flag-ların təsiri.
    """
    age = person.get("age")
    role = person.get("role")
    flags = person.get("flags", [])

    age_val = _get_age_weight(age)
    role_val = _get_role_weight(role)
    flags_val = _get_flags_weight(flags)

    return age_val + role_val + flags_val


def compute_track_loss(track: list) -> int:
    """
    Verilən relsdəki bütün şəxslərin dəyərlərinin cəmini qaytarır.
    Bu cəmi 'itirilən dəyər' kimi interpretasiya edirik.
    """
    return sum(compute_person_value(p) for p in track)

def compute_person_value_with_rules(
    person: dict,
    age_weights: dict,
    role_weights: dict,
    flag_weights: dict
) -> int:
    age = person.get("age")
    role = person.get("role")
    flags = person.get("flags", [])

    age_val = age_weights.get(age, 1) if age is not None else 1
    role_val = role_weights.get(role, 1) if role is not None else 1

    flags_val = 0
    for f in flags:
        flags_val += flag_weights.get(f, 0)

    return age_val + role_val + flags_val


def compute_track_loss_with_rules(
    track: list,
    age_weights: dict,
    role_weights: dict,
    flag_weights: dict
) -> int:
    return sum(
        compute_person_value_with_rules(p, age_weights, role_weights, flag_weights)
        for p in track
    )


def track_has_age(track: list, age: str) -> bool:
    """Verilən track-də müəyyən yaş qrupundan heç olmasa 1 nəfər varmı?"""
    return any(p.get("age") == age for p in track)


def track_count_flag(track: list, flag: str) -> int:
    """Verilən track-də müəyyən flag-ə malik neçə nəfər var?"""
    return sum(1 for p in track if flag in p.get("flags", []))


def track_count_any_flag(track: list, flags: list) -> int:
    """Verilən track-də flags siyahısından hər hansı birinə malik neçə nəfər var?"""
    return sum(
        1
        for p in track
        for f in p.get("flags", [])
        if f in flags
    )

def decide_deontological(
    track1: list,
    track2: list,
    variant: str,
    t1_loss: int,
    t2_loss: int,
    t1_count: int,
    t2_count: int
) -> tuple[int, str]:
    """
    Deontoloji etik variantlara əsasən qərar verir.
    Qayıdır: (chosen_track, reason)
    chosen_track = qurban verilən rels (1 və ya 2).
    """

    # Variant 1: Non-intervention – müdaxilə etmə
    if variant == "non_intervention":
        # Sadə model: default olaraq lever toxunulmur, trolley Track 1 üzrə gedir.
        chosen_track = 1
        reason = (
            "Deontoloji (müdaxilə etmə prinsipi): Leverə toxunulmadı, "
            "trolley mövcud rels üzrə (Track 1) hərəkət etdi. Aktiv müdaxilə edilmədi."
        )
        return chosen_track, reason

    # Variant 2: Uşaqları qorumaq (protect_children)
    if variant == "protect_children":
        has_child1 = track_has_age(track1, "child")
        has_child2 = track_has_age(track2, "child")

        if has_child1 and not has_child2:
            # Track 1-də uşaq var, Track 2-də yoxdur → Track 2 qurban verilsin
            chosen_track = 2
            reason = (
                "Deontoloji (uşaqları qorumaq): Uşaqlar olan rels qurban verilə bilməz. "
                "Track 1-də uşaq var, Track 2-də yoxdur, buna görə Track 2 qurban verildi."
            )
            return chosen_track, reason
        elif has_child2 and not has_child1:
            chosen_track = 1
            reason = (
                "Deontoloji (uşaqları qorumaq): Uşaqlar olan rels qurban verilə bilməz. "
                "Track 2-də uşaq var, Track 1-də yoxdur, buna görə Track 1 qurban verildi."
            )
            return chosen_track, reason
        # Hər ikisində ya var, ya da heç birində yoxdur → fallback utilitarian məntiqə
        # Fallback: etik dəyər itkisinə baxaq
        if t1_loss < t2_loss:
            chosen_track = 1
            reason = (
                "Deontoloji (uşaqlar eyni vəziyyətdədir), fallback utilitarian: "
                f"Track 1 itkiləri = {t1_loss}, Track 2 itkiləri = {t2_loss}. "
                "Daha az dəyər itkisi üçün Track 1 qurban verildi."
            )
        elif t2_loss < t1_loss:
            chosen_track = 2
            reason = (
                "Deontoloji (uşaqlar eyni vəziyyətdədir), fallback utilitarian: "
                f"Track 2 itkiləri = {t2_loss}, Track 1 itkiləri = {t1_loss}. "
                "Daha az dəyər itkisi üçün Track 2 qurban verildi."
            )
        else:
            chosen_track = 1
            reason = (
                "Deontoloji (uşaqlar eyni vəziyyətdədir), "
                f"etik dəyər itkisi də eynidir ({t1_loss}). Default olaraq Track 1 seçildi."
            )
        return chosen_track, reason

    # Variant 3: Günahsızları qorumaq (protect_innocent)
    if variant == "protect_innocent":
        guilty_flags = ["guilty", "law_breaker"]

        guilty_t1 = track_count_any_flag(track1, guilty_flags)
        guilty_t2 = track_count_any_flag(track2, guilty_flags)

        if guilty_t1 > guilty_t2:
            # Track 1-də daha çox günahkar var → onu qurban vermək "etik" sayılır
            chosen_track = 1
            reason = (
                "Deontoloji (günahsızları qorumaq): Track 1-də daha çox günahkar var, "
                "ona görə Track 1 qurban verildi ki, daha çox günahsız xilas olsun."
            )
            return chosen_track, reason
        elif guilty_t2 > guilty_t1:
            chosen_track = 2
            reason = (
                "Deontoloji (günahsızları qorumaq): Track 2-də daha çox günahkar var, "
                "ona görə Track 2 qurban verildi."
            )
            return chosen_track, reason

        # Günahkar sayı eynidirsə → fallback utilitarian (itkiyə baxırıq)
        if t1_loss < t2_loss:
            chosen_track = 1
            reason = (
                "Deontoloji (günahkar sayı eyni), fallback utilitarian: "
                f"Track 1 itkiləri = {t1_loss}, Track 2 itkiləri = {t2_loss}. "
                "Daha az etik dəyər itkisi üçün Track 1 qurban verildi."
            )
        elif t2_loss < t1_loss:
            chosen_track = 2
            reason = (
                "Deontoloji (günahkar sayı eyni), fallback utilitarian: "
                f"Track 2 itkiləri = {t2_loss}, Track 1 itkiləri = {t1_loss}. "
                "Daha az etik dəyər itkisi üçün Track 2 qurban verildi."
            )
        else:
            chosen_track = 1
            reason = (
                "Deontoloji (günahkar sayı və etik dəyər itkisi eynidir). "
                "Default olaraq Track 1 seçildi."
            )
        return chosen_track, reason

    # Variant 4: Zəif qrupları qorumaq (hamilə, əlil və s.)
    if variant == "protect_vulnerable":
        vulnerable_flags = ["pregnant", "disabled", "vulnerable"]

        v1 = track_count_any_flag(track1, vulnerable_flags)
        v2 = track_count_any_flag(track2, vulnerable_flags)

        if v1 > 0 and v2 == 0:
            # Track 1-də zəif qrup var, Track 2-də yoxdur → Track 2 qurban verilsin
            chosen_track = 2
            reason = (
                "Deontoloji (zəif qrupları qorumaq): Track 1-də hamilə/əlil/zəif "
                "qruplar var, ona görə Track 2 qurban verildi."
            )
            return chosen_track, reason
        elif v2 > 0 and v1 == 0:
            chosen_track = 1
            reason = (
                "Deontoloji (zəif qrupları qorumaq): Track 2-də hamilə/əlil/zəif "
                "qruplar var, ona görə Track 1 qurban verildi."
            )
            return chosen_track, reason

        # Hər ikisində eyni dərəcədə zəif qrup varsa → fallback utilitarian
        if t1_loss < t2_loss:
            chosen_track = 1
            reason = (
                "Deontoloji (zəif qruplar eyni vəziyyətdədir), fallback utilitarian: "
                f"Track 1 itkiləri = {t1_loss}, Track 2 itkiləri = {t2_loss}. "
                "Daha az etik dəyər itkisi üçün Track 1 qurban verildi."
            )
        elif t2_loss < t1_loss:
            chosen_track = 2
            reason = (
                "Deontoloji (zəif qruplar eyni vəziyyətdədir), fallback utilitarian: "
                f"Track 2 itkiləri = {t2_loss}, Track 1 itkiləri = {t1_loss}. "
                "Daha az etik dəyər itkisi üçün Track 2 qurban verildi."
            )
        else:
            chosen_track = 1
            reason = (
                "Deontoloji (zəif qruplar və etik dəyər itkisi eynidir). "
                "Default olaraq Track 1 seçildi."
            )
        return chosen_track, reason

    # Tanınmayan variant üçün fallback
    chosen_track = 1
    reason = (
        f"Deontoloji variant tanınmadı ({variant}). "
        "Default olaraq Track 1 seçildi."
    )
    return chosen_track, reason

def decide_custom(
    track1: list,
    track2: list,
    custom_rules: dict,
    t1_count: int,
    t2_count: int
) -> tuple[int, str, int, int]:
    """
    Custom utilitarian qaydalar əsasında qərar verir.
    custom_rules formatı:
    {
      "age_weights": {...},
      "role_weights": {...},
      "flag_weights": {...}
    }
    Qayıdır: (chosen_track, reason, t1_loss, t2_loss)
    """

    # Default cədvəlləri istifadəçi qaydaları ilə birləşdiririk
    age_w = merge_weights(AGE_WEIGHTS, custom_rules.get("age_weights"))
    role_w = merge_weights(ROLE_WEIGHTS, custom_rules.get("role_weights"))
    flag_w = merge_weights(FLAG_WEIGHTS, custom_rules.get("flag_weights"))

    # Hər track üçün itirilən etik dəyəri hesablayırıq
    t1_loss = compute_track_loss_with_rules(track1, age_w, role_w, flag_w)
    t2_loss = compute_track_loss_with_rules(track2, age_w, role_w, flag_w)

    if t1_loss < t2_loss:
        chosen_track = 1
        reason = (
            "Custom utilitarian mod: Sənin verdiyin ağırlıq cədvəlinə əsasən "
            f"Track 1 qurban verildi. Track 1 itkiləri = {t1_loss}, "
            f"Track 2 itkiləri = {t2_loss}."
        )
    elif t2_loss < t1_loss:
        chosen_track = 2
        reason = (
            "Custom utilitarian mod: Sənin verdiyin ağırlıq cədvəlinə əsasən "
            f"Track 2 qurban verildi. Track 2 itkiləri = {t2_loss}, "
            f"Track 1 itkiləri = {t1_loss}."
        )
    else:
        # Eynidirsə, saylara bax
        if t1_count < t2_count:
            chosen_track = 1
            reason = (
                "Custom utilitarian mod: Etik dəyər itkisi eynidir "
                f"({t1_loss}), amma Track 1-də daha az adam var "
                f"({t1_count} < {t2_count}). Ona görə Track 1 qurban verildi."
            )
        elif t2_count < t1_count:
            chosen_track = 2
            reason = (
                "Custom utilitarian mod: Etik dəyər itkisi eynidir "
                f"({t1_loss}), amma Track 2-də daha az adam var "
                f"({t2_count} < {t1_count}). Ona görə Track 2 qurban verildi."
            )
        else:
            chosen_track = 1
            reason = (
                "Custom utilitarian mod: Həm etik dəyər itkisi, həm də say eynidir. "
                "Default olaraq Track 1 qurban verildi."
            )

    return chosen_track, reason, t1_loss, t2_loss




def decide_scenario_v2(scenario: dict) -> dict:
    """
    Yeni data modeli üçün qərar verən funksiya.
    scenario formatı:
    {
      "track1": [ { "age": "...", "role": "...", "flags": [...] }, ... ],
      "track2": [ { "age": "...", "role": "...", "flags": [...] }, ... ],
      "mode": "utilitarian" / "deontological" / "custom" / ...
      "deon_variant": "non_intervention" / "protect_children" / "protect_innocent" / "protect_vulnerable"
      "custom_rules": {
          "age_weights": {...},
          "role_weights": {...},
          "flag_weights": {...}
      }
    }
    """

    track1 = scenario.get("track1", [])
    track2 = scenario.get("track2", [])
    mode = scenario.get("mode", "utilitarian")

    t1_count = len(track1)
    t2_count = len(track2)

    # Default utilitarian itkisini əvvəlcədən hesablayaq (deontoloji və s. üçün də istifadə olunur)
    t1_loss = compute_track_loss(track1)
    t2_loss = compute_track_loss(track2)

    # 1) Utilitarian mod (default ağırlıqlarla)
    if mode == "utilitarian":
        if t1_loss < t2_loss:
            chosen_track = 1
            reason = (
                f"Utilitarian mod (ağırlıqlı): Track 1 qurban verildi, çünki Track 1 itkiləri = {t1_loss}, "
                f"Track 2 itkiləri = {t2_loss}. Daha az etik dəyər itirilir."
            )
        elif t2_loss < t1_loss:
            chosen_track = 2
            reason = (
                f"Utilitarian mod (ağırlıqlı): Track 2 qurban verildi, çünki Track 2 itkiləri = {t2_loss}, "
                f"Track 1 itkiləri = {t1_loss}. Daha az etik dəyər itirilir."
            )
        else:
            # Etik dəyər itkisi bərabərdirsə, saylara baxaq
            if t1_count < t2_count:
                chosen_track = 1
                reason = (
                    f"Etik dəyər itkisi bərabərdir ({t1_loss}). Amma Track 1-də {t1_count}, "
                    f"Track 2-də {t2_count} nəfər var. Daha az say üçün Track 1 qurban verildi."
                )
            elif t2_count < t1_count:
                chosen_track = 2
                reason = (
                    f"Etik dəyər itkisi bərabərdir ({t1_loss}). Amma Track 2-də {t2_count}, "
                    f"Track 1-də {t1_count} nəfər var. Daha az say üçün Track 2 qurban verildi."
                )
            else:
                chosen_track = 1
                reason = (
                    f"Həm etik dəyər, həm də insan sayı bərabərdir "
                    f"(itki = {t1_loss}, say = {t1_count}). Default olaraq Track 1 seçildi."
                )

    # 2) Deontoloji mod
    elif mode == "deontological":
        deon_variant = scenario.get("deon_variant", "non_intervention")
        chosen_track, reason = decide_deontological(
            track1, track2, deon_variant, t1_loss, t2_loss, t1_count, t2_count
        )

    # 3) Custom utilitarian mod (sənin verdiyin ağırlıq cədvəlinə əsasən)
    elif mode == "custom":
        custom_rules = scenario.get("custom_rules", {})
        chosen_track, reason, t1_loss_custom, t2_loss_custom = decide_custom(
            track1, track2, custom_rules, t1_count, t2_count
        )
        # Cavabda custom loss-ları göstərmək üçün default loss-ları override edirik
        t1_loss = t1_loss_custom
        t2_loss = t2_loss_custom

    # 4) ML mode – mövcud ML modelini yeni dataya map edərək istifadə edirik
    elif mode == "ml":
        result = decide_ml_v2(track1, track2)
        chosen_track = result["chosen_track"]
        reason = "ML v2: " + result["reason"]
    # 5) Digər modlar (manual, compare və s.) – hələ implement olunmayıb
    else:
        chosen_track = 1
        reason = (
            f"Bu etik mod hələ implement olunmayıb (mode={mode}). "
            "Default olaraq Track 1 seçildi."
        )

    return {
        "chosen_track": chosen_track,
        "reason": reason,
        "track1_count": t1_count,
        "track2_count": t2_count,
        "track1_loss": t1_loss,
        "track2_loss": t2_loss
    }
