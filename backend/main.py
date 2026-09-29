from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import psycopg2
import os

# =========================================================
# PHISHGUARD AI - FASTAPI BACKEND
# =========================================================

app = FastAPI(
    title="PhishGuard AI",
    description="AI-Based Phishing and Online Scam Detection System",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg2.connect(database_url)

    # Local development
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="phishguardai",
        user="postgres",
        password="devanshi@1234"
    )

# =========================================================
# URL PHISHING MODEL
# =========================================================

MODEL_PATH = r"../ml/raw_url_phishing_model.pkl"

try:
    model = joblib.load(MODEL_PATH)
    model_status = "loaded"
except Exception as e:
    model = None
    model_status = f"error: {str(e)}"


# =========================================================
# SMS SCAM MODEL
# =========================================================

SMS_MODEL_PATH = r"../ml/sms_scam_model.pkl"

try:
    sms_model = joblib.load(SMS_MODEL_PATH)
    sms_model_status = "loaded"
except Exception as e:
    sms_model = None
    sms_model_status = f"error: {str(e)}"


# =========================================================
# REQUEST MODELS
# =========================================================

class URLRequest(BaseModel):
    url: str


class SMSRequest(BaseModel):
    message: str


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "PhishGuard AI Backend is running",
        "status": "success",
        "model": model_status,
        "sms_model": sms_model_status
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": model_status,
        "sms_model": sms_model_status
    }


# =========================================================
# DATABASE TEST
# =========================================================

@app.get("/api/db-test")
def database_test():

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM scan_history;"
        )

        count = cursor.fetchone()[0]

        return {
            "status": "success",
            "database": "connected",
            "scan_history_records": count
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# SCAN HISTORY API
# =========================================================

@app.get("/api/scan-history")
def get_scan_history():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                scan_type,
                input_text,
                prediction,
                risk_score,
                phishing_probability,
                legitimate_probability,
                scam_probability,
                safe_probability,
                created_at
            FROM scan_history
            ORDER BY created_at DESC
            """
        )

        rows = cursor.fetchall()

        history = []

        for row in rows:

            history.append(
                {
                    "id": row[0],
                    "type": row[1],
                    "input": row[2],
                    "prediction": row[3],
                    "risk_score": float(row[4]),
                    "phishing_probability": (
                        float(row[5])
                        if row[5] is not None
                        else None
                    ),
                    "legitimate_probability": (
                        float(row[6])
                        if row[6] is not None
                        else None
                    ),
                    "scam_probability": (
                        float(row[7])
                        if row[7] is not None
                        else None
                    ),
                    "safe_probability": (
                        float(row[8])
                        if row[8] is not None
                        else None
                    ),
                    "created_at": (
                        row[9].isoformat()
                        if row[9]
                        else None
                    )
                }
            )

        return {
            "total": len(history),
            "history": history
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch scan history: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# CLEAR SCAN HISTORY
# =========================================================

@app.delete("/api/scan-history")
def clear_scan_history():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM scan_history"
        )

        conn.commit()

        return {
            "status": "success",
            "message": "Scan history cleared successfully"
        }

    except Exception as e:

        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear scan history: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# URL PHISHING ANALYSIS
# =========================================================

@app.post("/api/analyze-url")
def analyze_url(request: URLRequest):

    url = request.url.strip()

    # -----------------------------------------------------
    # EMPTY URL CHECK
    # -----------------------------------------------------

    if not url:

        raise HTTPException(
            status_code=400,
            detail="URL cannot be empty"
        )

    # -----------------------------------------------------
    # MODEL CHECK
    # -----------------------------------------------------

    if model is None:

        raise HTTPException(
            status_code=500,
            detail="ML model could not be loaded"
        )

    # -----------------------------------------------------
    # AI PREDICTION
    # -----------------------------------------------------

    prediction = int(
        model.predict([url])[0]
    )

    probabilities = model.predict_proba([url])[0]

    classes = list(model.classes_)

    phishing_probability = float(
        probabilities[classes.index(0)]
    )

    legitimate_probability = float(
        probabilities[classes.index(1)]
    )

    # -----------------------------------------------------
    # TRUSTED OFFICIAL HOMEPAGE CHECK
    # -----------------------------------------------------

    from urllib.parse import urlparse

    parsed_url = urlparse(url)

    hostname = (
        parsed_url.hostname or ""
    ).lower()

    if hostname.startswith("www."):

        base_domain = hostname[4:]

    else:

        base_domain = hostname

    trusted_homepages = {
        "google.com",
        "microsoft.com",
        "amazon.com",
        "apple.com",
        "facebook.com",
        "instagram.com",
        "netflix.com",
        "paypal.com"
    }

    is_trusted_homepage = (
        parsed_url.scheme.lower() == "https"
        and base_domain in trusted_homepages
        and parsed_url.path in ("", "/")
        and not parsed_url.query
        and not parsed_url.fragment
        and not parsed_url.username
        and not parsed_url.password
    )

    if is_trusted_homepage:

        prediction = 1

        phishing_probability = 0.0

        legitimate_probability = 1.0

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    if prediction == 0:

        result = "PHISHING"

        risk_score = round(
            phishing_probability * 100,
            2
        )

    else:

        result = "LEGITIMATE"

        risk_score = round(
            phishing_probability * 100,
            2
        )

    # -----------------------------------------------------
    # EXPLAINABLE AI
    # -----------------------------------------------------

    explanation = []

    lower_url = url.lower()

    # -----------------------------------------------------
    # SUSPICIOUS URL INDICATORS
    # -----------------------------------------------------

    if "@" in lower_url:

        explanation.append(
            "URL contains an @ symbol, which can be used to hide the actual destination"
        )

    if lower_url.count("-") >= 3:

        explanation.append(
            "URL contains multiple hyphens, which may indicate a suspicious or impersonation-style domain"
        )

    if len(url) > 75:

        explanation.append(
            "URL is unusually long and contains a large amount of information"
        )

    if not lower_url.startswith("https://"):

        explanation.append(
            "URL does not use HTTPS, so the connection may not be securely encrypted"
        )

    # -----------------------------------------------------
    # SUSPICIOUS KEYWORD DETECTION
    # -----------------------------------------------------

    suspicious_keywords = [
        "login",
        "verify",
        "verification",
        "secure",
        "account",
        "update",
        "confirm",
        "signin",
        "password",
        "bank",
        "payment"
    ]

    found_keywords = [
        keyword
        for keyword in suspicious_keywords
        if keyword in lower_url
    ]

    if prediction == 0 and found_keywords:

        explanation.append(
            "URL contains suspicious security-related keywords: "
            + ", ".join(found_keywords)
        )

    # -----------------------------------------------------
    # BRAND IMPERSONATION INDICATORS
    # -----------------------------------------------------

    known_brands = [
        "paypal",
        "google",
        "microsoft",
        "amazon",
        "apple",
        "facebook",
        "instagram",
        "netflix"
    ]

    brand_found = [
        brand
        for brand in known_brands
        if brand in lower_url
    ]

    if prediction == 0 and brand_found:

        explanation.append(
            "URL contains a known brand name, which may indicate a brand impersonation attempt"
        )

    # -----------------------------------------------------
    # AI MODEL FALLBACK
    # -----------------------------------------------------

    if prediction == 0 and not explanation:

        explanation.append(
            "AI model detected suspicious URL patterns"
        )

    # -----------------------------------------------------
    # LEGITIMATE URL
    # -----------------------------------------------------

    if prediction == 1 and not explanation:

        explanation.append(
            "No major suspicious pattern detected"
        )

    # -----------------------------------------------------
    # SAVE URL SCAN TO DATABASE
    # -----------------------------------------------------

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO scan_history
            (
                scan_type,
                input_text,
                prediction,
                risk_score,
                phishing_probability,
                legitimate_probability
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                "URL",
                url,
                result,
                risk_score,
                round(
                    phishing_probability * 100,
                    2
                ),
                round(
                    legitimate_probability * 100,
                    2
                )
            )
        )

        conn.commit()

    except Exception as e:

        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save URL scan: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {

        "prediction": result,

        "risk_score": risk_score,

        "phishing_probability": round(
            phishing_probability * 100,
            2
        ),

        "legitimate_probability": round(
            legitimate_probability * 100,
            2
        ),

        "explanation": explanation,

        "url": url
    }


# =========================================================
# SMS / EMAIL SCAM ANALYSIS
# =========================================================

@app.post("/api/analyze-sms")
def analyze_sms(request: SMSRequest):

    message = request.message.strip()

    # -----------------------------------------------------
    # EMPTY MESSAGE CHECK
    # -----------------------------------------------------

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    # -----------------------------------------------------
    # MODEL CHECK
    # -----------------------------------------------------

    if sms_model is None:

        raise HTTPException(
            status_code=500,
            detail="SMS scam detection model could not be loaded"
        )

    # -----------------------------------------------------
    # AI PREDICTION
    # -----------------------------------------------------

    prediction = int(
        sms_model.predict([message])[0]
    )

    probabilities = sms_model.predict_proba([message])[0]

    classes = list(
        sms_model.classes_
    )

    scam_probability = float(
        probabilities[classes.index(1)]
    )

    safe_probability = float(
        probabilities[classes.index(0)]
    )

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    if prediction == 1:

        result = "SCAM"

        risk_score = round(
            scam_probability * 100,
            2
        )

    else:

        result = "SAFE"

        risk_score = round(
            scam_probability * 100,
            2
        )

    # -----------------------------------------------------
    # EXPLANATION
    # -----------------------------------------------------

    explanation = []

    lower_message = message.lower()

    # -----------------------------------------------------
    # SUSPICIOUS KEYWORDS
    # -----------------------------------------------------

    suspicious_keywords = [
        "win",
        "winner",
        "prize",
        "reward",
        "claim",
        "urgent",
        "verify",
        "verification",
        "click",
        "free",
        "offer",
        "limited time",
        "account",
        "bank",
        "otp",
        "password",
        "blocked"
    ]

    found_keywords = [
        keyword
        for keyword in suspicious_keywords
        if keyword in lower_message
    ]

    if found_keywords:

        explanation.append(
            "Message contains suspicious keywords: "
            + ", ".join(found_keywords[:5])
        )

    # -----------------------------------------------------
    # FINANCIAL / ACCOUNT RELATED WARNING
    # -----------------------------------------------------

    financial_keywords = [
        "bank",
        "account",
        "payment",
        "money",
        "prize",
        "reward",
        "otp",
        "password"
    ]

    found_financial = [
        keyword
        for keyword in financial_keywords
        if keyword in lower_message
    ]

    if found_financial:

        explanation.append(
            "Message involves financial or account-related information: "
            + ", ".join(found_financial[:4])
        )

    # -----------------------------------------------------
    # WEBSITE LINK DETECTION
    # -----------------------------------------------------

    has_link = (
        "http://" in lower_message
        or "https://" in lower_message
    )

    if has_link:

        explanation.append(
            "Message contains a website link"
        )

    # -----------------------------------------------------
    # CLICK INSTRUCTION
    # -----------------------------------------------------

    if "click" in lower_message:

        explanation.append(
            "Message asks the user to click a link"
        )

    # -----------------------------------------------------
    # URGENCY DETECTION
    # -----------------------------------------------------

    urgency_words = [
        "urgent",
        "immediately",
        "limited time",
        "act now",
        "hurry",
        "blocked",
        "suspended"
    ]

    found_urgency = [
        word
        for word in urgency_words
        if word in lower_message
    ]

    if found_urgency:

        explanation.append(
            "Message uses urgent or pressure-based language: "
            + ", ".join(found_urgency[:4])
        )

    # -----------------------------------------------------
    # EXCLAMATION MARK
    # -----------------------------------------------------

    if "!" in message and not found_urgency:

        explanation.append(
            "Message uses attention-grabbing punctuation"
        )

    # -----------------------------------------------------
    # AI FALLBACK FOR SCAM
    # -----------------------------------------------------

    if prediction == 1 and not explanation:

        explanation.append(
            "AI model detected patterns commonly associated "
            "with scam messages"
        )

    # -----------------------------------------------------
    # SAFE MESSAGE
    # -----------------------------------------------------

    if prediction == 0 and not explanation:

        explanation.append(
            "No major suspicious pattern detected"
        )

    # -----------------------------------------------------
    # SAVE SMS SCAN TO DATABASE
    # -----------------------------------------------------

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO scan_history
            (
                scan_type,
                input_text,
                prediction,
                risk_score,
                scam_probability,
                safe_probability
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                "SMS",
                message,
                result,
                risk_score,
                round(
                    scam_probability * 100,
                    2
                ),
                round(
                    safe_probability * 100,
                    2
                )
            )
        )

        conn.commit()

    except Exception as e:

        if conn:
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save SMS scan: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "message": message,

        "prediction": result,

        "risk_score": risk_score,

        "scam_probability": round(
            scam_probability * 100,
            2
        ),

        "safe_probability": round(
            safe_probability * 100,
            2
        ),

        "model_status": "ready",

        "explanation": explanation
    }