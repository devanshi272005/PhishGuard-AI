from ucimlrepo import fetch_ucirepo
import pandas as pd

print("Loading PhiUSIIL dataset...")

dataset = fetch_ucirepo(id=967)

X = dataset.data.features
y = dataset.data.targets

df = pd.concat([X, y], axis=1)

print("Dataset loaded successfully!")
print("Shape:", df.shape)

# URL ke saath useful numerical features
feature_columns = [
    "URLLength",
    "DomainLength",
    "IsDomainIP",
    "TLDLength",
    "NoOfSubDomain",
    "NoOfObfuscatedChar",
    "NoOfLettersInURL",
    "NoOfDegitsInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "IsHTTPS",
    "LetterRatioInURL",
    "DegitRatioInURL",
    "ObfuscationRatio",
    "URLSimilarityIndex",
    "CharContinuationRate",
    "TLDLegitimateProb",
    "URLCharProb",
    "SpacialCharRatioInURL"
]
    

X = df[feature_columns]
y = df["label"]

print("\nSelected features:", len(feature_columns))
print("X shape:", X.shape)
print("y shape:", y.shape)

print("\nLabel distribution:")
print(y.value_counts())

print("\nFeature preparation completed successfully!")
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\nTraining Random Forest model...")

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("Model training completed!")

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print(f"\nModel Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

model_path = r"C:\phishguardai\PhishGuard-AI\ml\url_phishing_model.pkl"

joblib.dump(model, model_path)

print("\nURL model saved successfully at:")
print(model_path)