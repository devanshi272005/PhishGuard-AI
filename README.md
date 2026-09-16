# 🛡️ PhishGuard AI

## AI-Based Phishing & Scam Detection System

PhishGuard AI is an AI-powered cybersecurity application designed to detect
potentially malicious phishing URLs and scam messages.

The system uses Machine Learning and NLP-based text analysis to identify
suspicious patterns and provide a risk score with an explanation of the
detected threat.

---

## 🚀 Features

### 🔗 Phishing URL Detection
Analyzes website URLs and classifies them as:

- Legitimate
- Phishing

### 📱 SMS / Scam Detection
Analyzes SMS or text messages and identifies potentially fraudulent or scam
messages.

### 📊 Risk Score
Provides:

- Risk percentage
- Phishing probability
- Legitimate probability
- Scam probability
- Safe probability

### 🧠 Explainable Detection
Provides reasons behind the detection, such as:

- Suspicious keywords
- Urgency-based language
- Suspicious URL patterns
- Missing HTTPS
- Known brand-related patterns

### 🗂️ Scan History
Stores previous URL and message scans using PostgreSQL.

### 📈 Security Dashboard
Provides an overview of:

- URLs analyzed
- Phishing threats detected
- Messages analyzed
- Scams detected
- Phishing rate
- Scam rate
- Total threats

---

## 🏗️ Project Architecture

```text
PhishGuard AI
│
├── frontend/
│   └── React + Vite
│
├── backend/
│   └── FastAPI
│
├── ml/
│   ├── datasets/
│   ├── URL phishing model
│   └── SMS scam model
│
└── PostgreSQL Database

💻 Technology Stack

| Technology   | Purpose                    |
| ------------ | -------------------------- |
| Python       | Machine Learning & Backend |
| Scikit-learn | ML Models                  |
| NLP          | SMS/Message Analysis       |
| FastAPI      | Backend API                |
| React        | Frontend                   |
| Vite         | Frontend Development       |
| PostgreSQL   | Database                   |
| Pandas       | Data Processing            |
| JavaScript   | Frontend Logic             |

🔄 Working Process

User Input
    ↓
URL / SMS Analysis
    ↓
Machine Learning Model
    ↓
Threat Classification
    ↓
Risk Score
    ↓
Explanation
    ↓
Result + Scan History

🎯 Project Objectives

Detect phishing websites
Identify scam messages
Provide understandable threat explanations
Calculate security risk
Maintain scan history
Provide a simple cybersecurity dashboard

🔮 Future Scope

Possible future enhancements include:

Browser extension
Real-time website analysis
Advanced threat intelligence
Email phishing detection
Improved explainable AI
More advanced ML models
Real-time security alerts

