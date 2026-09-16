import pandas as pd
from sklearn.model_selection import train_test_split

# Dataset load karo
dataset_path = r"C:\phishguardai\PhishGuard-AI\ml\datasets\urls.csv"

df = pd.read_csv(dataset_path)

# Features aur target separate karo
X = df.drop("result", axis=1)
y = df["result"]

# 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Dataset loaded successfully!")
print("Total samples:", len(df))
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
print("Number of features:", X.shape[1])
print("\nClass distribution:")
print(y.value_counts())
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Random Forest model
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

print("\nTraining Random Forest model...")

model.fit(X_train, y_train)

print("Model training completed!")

# Test prediction
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print(f"\nModel Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save trained model
model_path = r"C:\phishguardai\PhishGuard-AI\ml\phishing_url_model.pkl"

joblib.dump(model, model_path)

print(f"\nModel saved successfully at:")
print(model_path)