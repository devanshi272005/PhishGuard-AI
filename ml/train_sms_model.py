import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# ==============================
# Load SMS Dataset
# ==============================

DATASET_PATH = r"C:\phishguardai\PhishGuard-AI\ml\datasets\SMSSpamCollection"

df = pd.read_csv(
    DATASET_PATH,
    sep="\t",
    header=None,
    names=["label", "message"]
)

print("Dataset shape:", df.shape)

print("\nLabel distribution:")
print(df["label"].value_counts())


# ==============================
# Prepare Data
# ==============================

X = df["message"].astype(str)

# spam = 1
# ham = 0
y = df["label"].map({
    "ham": 0,
    "spam": 1
})


# ==============================
# Train-Test Split
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ==============================
# TF-IDF + Logistic Regression
# ==============================

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
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


# ==============================
# Train Model
# ==============================

print("\nTraining SMS scam detection model...")

model.fit(X_train, y_train)


# ==============================
# Evaluation
# ==============================

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    target_names=["HAM (SAFE)", "SPAM (SCAM)"]
))


# ==============================
# Save Model
# ==============================

MODEL_PATH = r"C:\phishguardai\PhishGuard-AI\ml\sms_scam_model.pkl"

joblib.dump(model, MODEL_PATH)

print("\nModel saved successfully!")
print(MODEL_PATH)