import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

df = pd.read_csv("training_data.csv")
X_raw = df["command"]
y = df["label"]

vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=2000)
X = vectorizer.fit_transform(X_raw)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=["benign", "malicious"]))

joblib.dump(model, "rf_model.joblib")
joblib.dump(vectorizer, "tfidf_vectorizer.joblib")
print("Saved rf_model.joblib and tfidf_vectorizer.joblib")
