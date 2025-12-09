import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_trolley_v2():
    df = pd.read_csv("trolley_data_v2.csv")

    # son sütun hədəfdir
    y = df["chosen_track"]

    # son sütundan başqa hamısı feature-dır
    X = df.drop(columns=["chosen_track"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        random_state=42
    )

    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)
    print(f"Model Dəqiqliyi: {score * 100:.2f}%")

    joblib.dump(model, "trolley_model_v2.pkl")
    print("Yeni ML modeli trolley_model_v2.pkl olaraq saxlanıldı.")

if __name__ == "__main__":
    train_trolley_v2()
