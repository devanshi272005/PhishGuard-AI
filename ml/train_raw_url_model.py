import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# Dataset load
DATASET_PATH = r"C:\phishguardai\PhishGuard-AI\ml\datasets\phiusiil.csv"

df = pd.read_csv(DATASET_PATH)

print("Dataset shape:", df.shape)


# URL and label
X = df["URL"].astype(str).str.lower()
y = df["label"]


# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# Raw URL text model
model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            analyzer="char",
            ngram_range=(3, 5),
            min_df=2,
            max_features=50000,
            sublinear_tf=True
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )
    )
])


print("\nTraining model...")

model.fit(X_train, y_train)


# Evaluation
predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print(
    "\nModel Accuracy:",
    round(accuracy * 100, 2),
    "%"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions
    )
)


# Save model
MODEL_PATH = r"C:\phishguardai\PhishGuard-AI\ml\raw_url_phishing_model.pkl"

joblib.dump(
    model,
    MODEL_PATH
)

print("\nModel saved successfully!")

print(MODEL_PATH)