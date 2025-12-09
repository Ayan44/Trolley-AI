import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

def train_model():
    # CSV faylının yolunu təyin edirik
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "trolley_data.csv")

    # 1. Məlumatı oxu
    df = pd.read_csv(data_path)

    # 2. X (xüsusiyyətlər) və y (hədəf) böl
    feature_cols = [
        "t1_children", "t1_adults", "t1_elders",
        "t2_children", "t2_adults", "t2_elders"
    ]
    X = df[feature_cols]
    y = df["chosen_track"]

    # 3. Train/test bölməsi (sadəcə yoxlama üçün)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 4. Modeli yarat və öyrət
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)

    # 5. Sadə dəqiqlik göstəricisi (terminalda görmək üçün)
    accuracy = model.score(X_test, y_test)
    print(f"Test dəqiqliyi: {accuracy:.2f}")

    # 6. Modeli fayla yaz
    model_path = os.path.join(base_dir, "trolley_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saxlanıldı: {model_path}")

if __name__ == "__main__":
    train_model()
