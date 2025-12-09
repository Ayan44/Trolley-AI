import csv
import random

# Eyni nəticələri almaq üçün sabit toxum
random.seed(42)

# Yaş, rol və flag tipləri
AGE_TYPES = ["child", "teen", "adult", "elder"]
ROLE_TYPES = [
    "doctor", "nurse", "teacher", "engineer",
    "student", "unemployed", "retired",
    "pregnant_role",  # hamilə qadının rolu kimi
    "criminal", "thief", "other"
]
FLAG_TYPES = [
    "pregnant", "disabled", "innocent", "guilty",
    "law_breaker", "relative", "friend", "stranger",
    "saves_lives", "vulnerable"
]

# Etik ağırlıqlar – ai_model.py-də istifadə etdiklərimizə uyğundur
AGE_WEIGHTS = {
    "child": 4,
    "teen": 3,
    "young": 3,   # burada istifadə etməsək də saxlayırıq
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
    "pregnant_role": 3,
    "criminal": -1,
    "thief": 0,
    "other": 1
}

FLAG_WEIGHTS = {
    "pregnant": 3,
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

# CSV sütunları
HEADER = [
    # Track 1 – yaş
    "t1_child", "t1_teen", "t1_adult", "t1_elder",
    # Track 1 – rol
    "t1_doctor", "t1_nurse", "t1_teacher", "t1_engineer",
    "t1_student", "t1_unemployed", "t1_retired",
    "t1_pregnant_role", "t1_criminal", "t1_thief", "t1_other",
    # Track 1 – flags
    "t1_pregnant_flag", "t1_disabled_flag", "t1_innocent_flag",
    "t1_guilty_flag", "t1_law_breaker_flag", "t1_relative_flag",
    "t1_friend_flag", "t1_stranger_flag", "t1_saves_lives_flag",
    "t1_vulnerable_flag",

    # Track 2 – yaş
    "t2_child", "t2_teen", "t2_adult", "t2_elder",
    # Track 2 – rol
    "t2_doctor", "t2_nurse", "t2_teacher", "t2_engineer",
    "t2_student", "t2_unemployed", "t2_retired",
    "t2_pregnant_role", "t2_criminal", "t2_thief", "t2_other",
    # Track 2 – flags
    "t2_pregnant_flag", "t2_disabled_flag", "t2_innocent_flag",
    "t2_guilty_flag", "t2_law_breaker_flag", "t2_relative_flag",
    "t2_friend_flag", "t2_stranger_flag", "t2_saves_lives_flag",
    "t2_vulnerable_flag",

    # Hədəf
    "chosen_track"
]


def random_person():
    """
    Təsadüfi bir 'person' obyekti yaradır:
    {
      "age": ...,
      "role": ...,
      "flags": [...]
    }
    """
    # Yaş üçün sadə ehtimallar – uşaqlar bir az daha az, böyüklər daha çox
    age = random.choices(
        AGE_TYPES,
        weights=[2, 2, 4, 2],  # child, teen, adult, elder
        k=1
    )[0]

    # Rol üçün ehtimallar
    role = random.choices(
        ROLE_TYPES,
        weights=[2, 1, 2, 1, 2, 2, 1, 1, 1, 1, 1],
        k=1
    )[0]

    flags = []

    # Hamilə flag-i – yalnız adult/teen qadın rolu kimi təsəvvür edək
    if role == "pregnant_role":
        flags.append("pregnant")
        flags.append("vulnerable")

    # Bəzi rollar üçün tipik flag-lar
    if role == "doctor" or role == "nurse":
        flags.append("saves_lives")
        flags.append("innocent")
    if role == "teacher":
        flags.append("innocent")
    if role == "criminal":
        flags.append("guilty")
        flags.append("law_breaker")
    if role == "thief":
        flags.append("law_breaker")

    # Əlavə random flag-lar (innocent, disabled, relative, friend və s.)
    if "guilty" not in flags:
        # çox vaxt adamlar günahsızdır
        if random.random() < 0.7:
            flags.append("innocent")

    if random.random() < 0.15:
        flags.append("disabled")
        flags.append("vulnerable")

    # münasibət flag-ları
    r = random.random()
    if r < 0.1:
        flags.append("relative")
    elif r < 0.2:
        flags.append("friend")
    else:
        flags.append("stranger")

    # Unikal olsun
    flags = list(set(flags))

    return {
        "age": age,
        "role": role,
        "flags": flags
    }


def compute_person_value(person):
    """
    Eyni utilitarian dəyər funksiyası:
    yaş + rol + flag-lar ağırlığı.
    """
    age = person.get("age")
    role = person.get("role")
    flags = person.get("flags", [])

    age_val = AGE_WEIGHTS.get(age, 1)
    role_val = ROLE_WEIGHTS.get(role, 1)

    flags_val = 0
    for f in flags:
        flags_val += FLAG_WEIGHTS.get(f, 0)

    return age_val + role_val + flags_val


def generate_track(min_people=1, max_people=5):
    """
    Verilən say aralığında random track (şəxslər listi) yaradır.
    """
    n = random.randint(min_people, max_people)
    return [random_person() for _ in range(n)]


def track_to_features(prefix, persons):
    """
    Bir track-dəki şəxsləri CSV üçün feature-lərə çevirir.
    prefix: "t1_" və ya "t2_"
    """
    feat = {}

    # Bütün sütun adları üçün ilkin 0 dəyər
    if prefix == "t1_":
        base_cols = HEADER[0:25]
    else:
        base_cols = HEADER[25:50]

    for col in base_cols:
        feat[col] = 0

    # Şəxsləri say
    for p in persons:
        age = p.get("age")
        role = p.get("role")
        flags = p.get("flags", [])

        # Yaş
        if age == "child":
            feat[f"{prefix}child"] += 1
        elif age == "teen":
            feat[f"{prefix}teen"] += 1
        elif age == "adult":
            feat[f"{prefix}adult"] += 1
        elif age == "elder":
            feat[f"{prefix}elder"] += 1
        else:
            # bilinməyən yaş – adult kimi saya bilərik
            feat[f"{prefix}adult"] += 1

        # Rol
        role_key = role
        if role_key not in ROLE_WEIGHTS:
            role_key = "other"

        if role_key == "pregnant_role":
            feat[f"{prefix}pregnant_role"] += 1
        else:
            feat_key = f"{prefix}{role_key}"
            if feat_key in feat:
                feat[feat_key] += 1
            else:
                # hər ehtimala qarşı
                feat[f"{prefix}other"] += 1

        # Flags
        for f in flags:
            col_name = None
            if f in ["pregnant", "disabled", "innocent", "guilty",
                     "law_breaker", "relative", "friend", "stranger",
                     "saves_lives", "vulnerable"]:
                col_name = f"{prefix}{f}_flag"
            if col_name and col_name in feat:
                feat[col_name] += 1

    return feat


def compute_track_loss(persons):
    return sum(compute_person_value(p) for p in persons)


def generate_scenario_row():
    """
    Tək bir ssenari yaradır, feature-lərə çevirir və chosen_track hesablayır.
    chosen_track = qurban verilən rels (1 və ya 2).
    """
    track1 = generate_track()
    track2 = generate_track()

    t1_loss = compute_track_loss(track1)
    t2_loss = compute_track_loss(track2)

    # Etik qərar – daha az dəyər itirilən track qurban verilsin
    if t1_loss < t2_loss:
        chosen_track = 1
    elif t2_loss < t1_loss:
        chosen_track = 2
    else:
        # eyni olarsa – az adam olan qurban verilsin
        if len(track1) < len(track2):
            chosen_track = 1
        elif len(track2) < len(track1):
            chosen_track = 2
        else:
            # tam eyni isə random
            chosen_track = random.choice([1, 2])

    # Feature-ləri yığ
    feat_t1 = track_to_features("t1_", track1)
    feat_t2 = track_to_features("t2_", track2)

    row = []

    # HEADER sırasına uyğun doldururuq
    for col in HEADER:
        if col == "chosen_track":
            row.append(chosen_track)
        else:
            row.append(feat_t1.get(col, feat_t2.get(col, 0)))

    return row


def main():
    num_rows = 200  # istəsən 100, 300 və s. edə bilərsən

    with open("trolley_data_v2.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)

        for _ in range(num_rows):
            row = generate_scenario_row()
            writer.writerow(row)

    print(f"{num_rows} sətirlik trolley_data_v2.csv yaradıldı.")


if __name__ == "__main__":
    main()
