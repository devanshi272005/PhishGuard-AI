import { useEffect, useState } from "react";
import "./App.css";

function App() {
  // =========================
  // URL STATES
  // =========================
  const [url, setUrl] = useState("");
  const [urlResult, setUrlResult] = useState(null);
  const [urlLoading, setUrlLoading] = useState(false);
  const [urlError, setUrlError] = useState("");

  // =========================
  // SMS STATES
  // =========================
  const [message, setMessage] = useState("");
  const [smsResult, setSmsResult] = useState(null);
  const [smsLoading, setSmsLoading] = useState(false);
  const [smsError, setSmsError] = useState("");

  // =========================
  // DASHBOARD COUNTERS
  // =========================
  const [urlCount, setUrlCount] = useState(0);
  const [phishingCount, setPhishingCount] = useState(0);
  const [messageCount, setMessageCount] = useState(0);
  const [scamCount, setScamCount] = useState(0);

  // =========================
  // SCAN HISTORY
  // =========================
  const [scanHistory, setScanHistory] = useState([]);

  // =========================
  // RISK LEVEL
  // =========================
  const getRiskLevel = (score) => {
    if (score >= 70) return "High Risk";
    if (score >= 30) return "Medium Risk";
    return "Low Risk";
  };

  // =========================
  // RISK BAR WIDTH
  // =========================
  const getRiskWidth = (score) => {
    const value = Number(score) || 0;
    return `${Math.min(Math.max(value, 0), 100)}%`;
  };

  // =========================
  // RISK BAR COLOR CLASS
  // =========================
  const getRiskClass = (score) => {
    if (score >= 70) return "risk-high";
    if (score >= 30) return "risk-medium";
    return "risk-low";
  };

  // =========================
  // FETCH SCAN HISTORY
  // =========================
  const fetchScanHistory = async () => {
    try {
      const response = await fetch(
        "https://phishguardai-backend-j05x.onrender.com/api/scan-history"
      );

      const data = await response.json();
      setScanHistory(data);
      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to fetch scan history"
        );
      }

      const history = data.history || [];

      // Update history
      setScanHistory(history);

      // =========================
      // UPDATE DASHBOARD COUNTERS
      // =========================

      // Total URLs
      setUrlCount(
        history.filter(
          (scan) => scan.type === "URL"
        ).length
      );

      // Phishing URLs
      setPhishingCount(
        history.filter(
          (scan) =>
            scan.type === "URL" &&
            scan.prediction === "PHISHING"
        ).length
      );

      // Total SMS
      setMessageCount(
        history.filter(
          (scan) => scan.type === "SMS"
        ).length
      );

      // Scam SMS
      setScamCount(
        history.filter(
          (scan) =>
            scan.type === "SMS" &&
            scan.prediction === "SCAM"
        ).length
      );
    } catch (error) {
      console.error(
        "History fetch error:",
        error
      );
    }
  };

  // =========================
  // LOAD HISTORY ON PAGE LOAD
  // =========================
  useEffect(() => {
    fetchScanHistory();
  }, []);

  // =========================
  // CLEAR SCAN HISTORY
  // =========================
  const clearScanHistory = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to clear all scan history?"
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        "https://phishguardai-backend-j05x.onrender.com/api/scan-history",
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to clear history"
        );
      }

      // Clear frontend history
      setScanHistory([]);

      // Reset dashboard counters
      setUrlCount(0);
      setPhishingCount(0);
      setMessageCount(0);
      setScamCount(0);

      // Clear currently displayed results
      setUrlResult(null);
      setSmsResult(null);

      // Clear input fields
      setUrl("");
      setMessage("");

      // Clear errors
      setUrlError("");
      setSmsError("");
    } catch (error) {
      console.error(
        "Clear history error:",
        error
      );

      alert(
        "Failed to clear scan history."
      );
    }
  };

  // =========================
  // URL ANALYSIS
  // =========================
  const analyzeURL = async () => {
    const inputURL = url.trim();

    if (!inputURL) {
      setUrlError("Please enter a URL");
      setUrlResult(null);
      return;
    }

    // Add HTTPS if user does not enter protocol
    let validURL = inputURL;

    if (
      !validURL
        .toLowerCase()
        .startsWith("http://") &&
      !validURL
        .toLowerCase()
        .startsWith("https://")
    ) {
      validURL = "https://" + validURL;
    }
    // Validate URL
try {
  const parsedURL = new URL(validURL);

  if (!parsedURL.hostname.includes(".")) {
    setUrlError("Please enter a valid URL");
    setUrlResult(null);
    return;
  }
} catch {
  setUrlError("Please enter a valid URL");
  setUrlResult(null);
  return;
}
    
    setUrlLoading(true);
    setUrlError("");
    setUrlResult(null);

    try {
      const response = await fetch(
        "https://phishguardai-backend-j05x.onrender.com/api/analyze-url",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: validURL,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Something went wrong"
        );
      }

      // Show result
      setUrlResult(data);

      // Refresh history and dashboard
      await fetchScanHistory();
    } catch (err) {
      console.error(err);

      setUrlError(
        "Backend se connection nahi ho pa raha. Check karo ki FastAPI server running hai."
      );
    } finally {
      setUrlLoading(false);
    }
  };

  // =========================
  // SMS ANALYSIS
  // =========================
  const analyzeSMS = async () => {
    const inputMessage = message.trim();

    if (!inputMessage) {
      setSmsError("Please enter a message");
      setSmsResult(null);
      return;
    }

    setSmsLoading(true);
    setSmsError("");
    setSmsResult(null);

    try {
      const response = await fetch(
        "https://phishguardai-backend-j05x.onrender.com/api/analyze-sms",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: inputMessage,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Something went wrong"
        );
      }

      // Show result
      setSmsResult(data);

      // Refresh history and dashboard
      await fetchScanHistory();
    } catch (err) {
      console.error(err);

      setSmsError(
        "Backend se connection nahi ho pa raha. Check karo ki FastAPI server running hai."
      );
    } finally {
      setSmsLoading(false);
    }
  };

  return (
    <div className="app">

      {/* ================= HEADER ================= */}
      <header className="header">
        <div className="header-content">

          <div>
            <h1>🛡️ PhishGuard AI</h1>
            <p>
              AI-Powered Phishing & Online Scam Detection
            </p>
          </div>

          <div className="status">
            <span className="status-dot"></span>
            System Online
          </div>

        </div>
      </header>

      <main className="container">

  {/* ================= DASHBOARD ================= */}
  <section className="dashboard">

    <div className="dashboard-header">
      <div>
        <h2>Security Dashboard</h2>
        <p>Real-time overview of your phishing and scam detection activity</p>
      </div>

      <div className="dashboard-status">
        <span className="status-dot"></span>
        System Protected
      </div>
    </div>


    {/* ================= DASHBOARD CARDS ================= */}
    <div className="dashboard-cards">

      {/* URLs */}
      <div className="dashboard-card security-card">

        <div className="card-top">
          <span className="card-icon">🔗</span>
          <span className="card-status">URL SCANS</span>
        </div>

        <h3>URLs Scanned</h3>

        <strong>{urlCount}</strong>

        <p>Websites analyzed by AI</p>

      </div>


      {/* PHISHING */}
      <div className="dashboard-card threat-card">

        <div className="card-top">
          <span className="card-icon">🚨</span>
          <span className="card-status">THREATS</span>
        </div>

        <h3>Phishing Detected</h3>

        <strong>{phishingCount}</strong>

        <p>Malicious URLs detected</p>

      </div>


      {/* MESSAGES */}
      <div className="dashboard-card message-card">

        <div className="card-top">
          <span className="card-icon">💬</span>
          <span className="card-status">MESSAGE SCANS</span>
        </div>

        <h3>Messages Scanned</h3>

        <strong>{messageCount}</strong>

        <p>SMS & messages analyzed</p>

      </div>


      {/* SCAMS */}
      <div className="dashboard-card scam-card">

        <div className="card-top">
          <span className="card-icon">⚠️</span>
          <span className="card-status">ALERTS</span>
        </div>

        <h3>Scams Detected</h3>

        <strong>{scamCount}</strong>

        <p>Potential scam messages</p>

      </div>

    </div>


    {/* ================= DETECTION SUMMARY ================= */}
    <div className="detection-summary">

      <div className="summary-header">

        <div>
          <h3>🛡️ Detection Summary</h3>

          <p>
            Overview of threats identified by PhishGuard AI
          </p>
        </div>

      </div>


      <div className="summary-stats">

        <div className="summary-item">

          <span>Phishing Rate</span>

          <strong>
            {urlCount > 0
              ? ((phishingCount / urlCount) * 100).toFixed(1)
              : "0"}
            %
          </strong>

        </div>


        <div className="summary-item">

          <span>Scam Rate</span>

          <strong>
            {messageCount > 0
              ? ((scamCount / messageCount) * 100).toFixed(1)
              : "0"}
            %
          </strong>

        </div>


        <div className="summary-item">

          <span>Total Threats</span>

          <strong>
            {phishingCount + scamCount}
          </strong>

        </div>


        <div className="summary-item">

          <span>Security Status</span>

          <strong className="secure-status">
            {phishingCount + scamCount === 0
              ? "SECURE"
              : "MONITOR"}
          </strong>

        </div>

      </div>

    </div>

  </section>


  {/* ================= SCAN HISTORY ================= */}
        {/* ================= SCAN HISTORY ================= */}
        <div className="history-section">

          <div className="history-header">

            <h2>Scan History</h2>

            <button
              className="clear-history-btn"
              onClick={clearScanHistory}
            >
              Clear History
            </button>

          </div>

          {scanHistory.length === 0 ? (
            <p>No scans performed yet.</p>
          ) : (
            scanHistory.map(
              (scan, index) => (
                <div
                  className="history-card"
                  key={scan.id || index}
                >

                  <div>
                    <strong>
                      {scan.type}
                    </strong>

                    <p>
                      {scan.input}
                    </p>
                  </div>

                  <div>
                    <strong>
                      {scan.prediction}
                    </strong>

                    <p>
                      Risk:{" "}
                      {scan.risk_score}%
                    </p>
                  </div>

                </div>
              )
            )
          )}

        </div>

        {/* ================= URL DETECTOR ================= */}
        <section className="card">

          <div className="card-header">

            <div>
              <h2>
                🔗 Website / URL Scanner
              </h2>

              <p>
                Check whether a website URL
                is legitimate or phishing.
              </p>
            </div>

          </div>

          <div className="url-input-group">
  <input
    type="text"
    placeholder="Enter website URL e.g. google.com"
    value={url}
    onChange={(e) =>
      setUrl(e.target.value)
    }
    onKeyDown={(e) => {
      if (e.key === "Enter") {
        analyzeURL();
      }
    }}
  />

  <button
    className="analyze-url-btn"
    onClick={analyzeURL}
    disabled={urlLoading}
  >
    {urlLoading
      ? "Analyzing..."
      : "Analyze URL"}
  </button>
</div>

          {urlError && (
            <div className="error-message">
              ❌ {urlError}
            </div>
          )}

          {/* URL RESULT */}
          {urlResult && (
            <div
              className={`result-box ${
                urlResult.prediction ===
                "PHISHING"
                  ? "danger"
                  : "safe"
              }`}
            >

              <div className="result-header">

                <div>
                  <span className="result-label">
                    Detection Result
                  </span>

                  <h3>
                    {urlResult.prediction ===
                    "PHISHING"
                      ? "🚨 PHISHING"
                      : "✅ LEGITIMATE"}
                  </h3>
                </div>

                <div className="risk-badge">
                  {getRiskLevel(
                    urlResult.risk_score
                  )}
                </div>

              </div>

              {/* Risk Score */}
              <div className="detail-box risk-score-box">

                <div className="detail-row">

                  <span>Risk Score</span>

                  <strong>
                    {urlResult.risk_score}%
                  </strong>

                </div>

                <div className="risk-bar">

                  <div
                    className={`risk-bar-fill ${getRiskClass(
                      urlResult.risk_score
                    )}`}
                    style={{
                      width:
                        getRiskWidth(
                          urlResult.risk_score
                        ),
                    }}
                  ></div>

                </div>

              </div>

             <div className="result-details">

  <div className="detail-box phishing-detail">
    <div className="detail-label">
      <span className="detail-icon">🚨</span>
      <span>Phishing Probability</span>
    </div>

    <strong>
      {urlResult.phishing_probability}%
    </strong>

    <div className="probability-bar">
      <div
        className="probability-fill phishing-fill"
        style={{
          width: `${urlResult.phishing_probability}%`
        }}
      ></div>
    </div>
  </div>

  <div className="detail-box legitimate-detail">
    <div className="detail-label">
      <span className="detail-icon">🛡️</span>
      <span>Legitimate Probability</span>
    </div>

    <strong>
      {urlResult.legitimate_probability}%
    </strong>

    <div className="probability-bar">
      <div
        className="probability-fill legitimate-fill"
        style={{
          width: `${urlResult.legitimate_probability}%`
        }}
      ></div>
    </div>
  </div>

</div>

              <div className="analyzed-value">

                <span>
                  Analyzed URL
                </span>

                <strong>
                  {urlResult.url}
                </strong>

              </div>

              {/* Explanation */}
              <div className="explanation">

                <strong>
                  🔍 Why this result?
                </strong>

                <ul>
                  {urlResult.explanation &&
                    urlResult.explanation.map(
                      (reason, index) => (
                        <li key={index}>
                          {reason}
                        </li>
                      )
                    )}
                </ul>

              </div>

            </div>
          )}

        </section>

        {/* ================= SMS DETECTOR ================= */}
        <section className="card">

          <div className="card-header">

            <div>

              <h2>
                💬 SMS / Message Scanner
              </h2>

              <p>
                Detect scam, spam and
                suspicious messages using AI.
              </p>

            </div>

          </div>

          <div className="message-input">

            <textarea
              placeholder="Enter SMS or message here..."
              value={message}
              onChange={(e) =>
                setMessage(e.target.value)
              }
              rows="6"
            ></textarea>

            <button
              onClick={analyzeSMS}
              disabled={smsLoading}
            >
              {smsLoading
                ? "Analyzing..."
                : "Analyze Message"}
            </button>

          </div>

          {smsError && (
            <div className="error-message">
              ❌ {smsError}
            </div>
          )}

          {/* SMS RESULT */}
          {smsResult && (
            <div
              className={`result-box ${
                smsResult.prediction ===
                "SCAM"
                  ? "danger"
                  : "safe"
              }`}
            >

              <div className="result-header">

                <div>

                  <span className="result-label">
                    Detection Result
                  </span>

                  <h3>
                    {smsResult.prediction ===
                    "SCAM"
                      ? "🚨 SCAM"
                      : "✅ SAFE"}
                  </h3>

                </div>

                <div className="risk-badge">

                  {getRiskLevel(
                    smsResult.risk_score
                  )}

                </div>

              </div>

              {/* Risk Score */}
              <div className="detail-box risk-score-box">

                <div className="detail-row">

                  <span>
                    Risk Score
                  </span>

                  <strong>
                    {smsResult.risk_score}%
                  </strong>

                </div>

                <div className="risk-bar">

                  <div
                    className={`risk-bar-fill ${getRiskClass(
                      smsResult.risk_score
                    )}`}
                    style={{
                      width:
                        getRiskWidth(
                          smsResult.risk_score
                        ),
                    }}
                  ></div>

                </div>

              </div>

              <div className="result-details">

                <div className="detail-box">

                  <span>
                    Scam Probability
                  </span>

                  <strong>
                    {
                      smsResult.scam_probability
                    }%
                  </strong>

                </div>

                <div className="detail-box">

                  <span>
                    Safe Probability
                  </span>

                  <strong>
                    {
                      smsResult.safe_probability
                    }%
                  </strong>

                </div>

              </div>

              <div className="analyzed-value">

                <span>
                  Analyzed Message
                </span>

                <strong>
                  {smsResult.message}
                </strong>

              </div>

              {/* Explanation */}
              <div className="explanation">

                <strong>
                  🔍 Why this result?
                </strong>

                <ul>

                  {smsResult.explanation &&
                    smsResult.explanation.map(
                      (reason, index) => (
                        <li key={index}>
                          {reason}
                        </li>
                      )
                    )}

                </ul>

              </div>

            </div>
          )}

        </section>

        {/* ================= FOOTER INFO ================= */}
        <section className="info-section">

          <div className="info-card">

            <span>🤖</span>

            <h3>
              AI Powered
            </h3>

            <p>
              Machine learning models analyze
              URLs and messages for suspicious
              patterns.
            </p>

          </div>

          <div className="info-card">

            <span>🔒</span>

            <h3>
              Security Focused
            </h3>

            <p>
              Helps users identify potentially
              dangerous websites and scam
              messages.
            </p>

          </div>

          <div className="info-card">

            <span>⚡</span>

            <h3>
              Fast Detection
            </h3>

            <p>
              Get an AI-based risk assessment
              within seconds.
            </p>

          </div>

        </section>

      </main>

      <footer>

        <p>
          © 2026 PhishGuard AI —
          AI-Based Phishing & Scam Detection
        </p>

      </footer>

    </div>
  );
}

export default App;