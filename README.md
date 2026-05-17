# 🛡️ Sentinel AI - Enterprise Cyber-Security System

**Advanced AI-powered threat detection and prevention system** with real-time scanning, threat analysis, and comprehensive security monitoring.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Dashboard](#dashboard)
- [Models](#models)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)

---

## 🎯 Overview

Sentinel AI is an enterprise-ready autonomous cyber-security system designed to detect and prevent malware, phishing attacks, and security threats using hybrid AI models. The system combines:

- **Machine Learning Models**: Trained RandomForest & HistGradientBoosting classifiers
- **Rule-Based Detection**: 10+ heuristic indicators for URL and file analysis
- **Real-Time Scanning**: FastAPI backend with sub-second response times
- **Premium Dashboard**: Streamlit UI with modern visual design and threat visualization
- **Fallback Intelligence**: Heuristic scoring when models unavailable

---

## ✨ Key Features

### 🔍 Multi-Vector Threat Detection
- **Malware Detection**: File byte histogram analysis + entropy detection + suspicious string matching
- **Phishing Detection**: URL pattern analysis + transformer embeddings + keyword detection
- **Text Analysis**: Communication scanning for keywords, misspellings, and embedded URLs
- **Hybrid Scoring**: Combines ML model confidence with rule-based indicators (max-based)

### 🎨 Premium Dashboard
- Clean, modern Streamlit interface with gradient cards
- Real-time threat visualization with decision badges (BLOCKED/SUSPICIOUS/ALLOWED)
- Indicator chips (blue for risks, yellow for keywords, red for misspellings)
- Per-URL analysis with score breakdown
- System statistics and threat logs

### 🚀 API Service
- **FastAPI** backend running on `http://localhost:8000`
- RESTful endpoints for URL scanning, file analysis, text processing
- Health check and statistics endpoints
- Real-time response with detailed threat indicators

### 🤖 Intelligent Fallback System
- Heuristic URL scoring (HTTPS validation, IP detection, phishing keywords)
- File heuristics (MZ header, entropy, suspicious strings)
- Transformer embedding fallback for phishing detection
- Ensures system reliability even if models fail

### 🔐 3-State Security Decisions
- **ALLOWED** (score < 0.35): Safe to proceed
- **SUSPICIOUS** (0.35 ≤ score ≤ 0.60): Flag for review
- **BLOCKED** (score > 0.60): Prevent execution
- Safety-first: Hard risk indicators bump score to minimum threshold

---

## 🏗️ Architecture

```
Sentinel AI System
├── FastAPI Backend (Port 8000)
│   ├── URL Scanning Engine
│   ├── File Analysis Module
│   ├── Text Analysis Pipeline
│   └── Health & Stats Endpoints
│
├── ML Models Layer
│   ├── Phishing Detector (transformer embeddings + classifier)
│   ├── Malware Analyzer (byte histogram + heuristics)
│   └── Hybrid Scoring Engine (ML + Rules)
│
├── Streamlit Dashboard (Port 8501)
│   ├── File & URL Scanner Tab
│   ├── Communications Analyzer Tab
│   └── System Stats Tab
│
└── Training Pipeline
    ├── Malware Trainer (RandomForest/HistGradientBoosting)
    ├── Phishing Trainer (Transformer embeddings)
    └── AutoML Integration
```

---

## 💾 Installation

### Prerequisites
- Python 3.11+
- Windows PowerShell or Command Prompt
- 2GB+ RAM recommended
- Internet connection (for model downloads)

### Quick Start

1. **Clone/Extract the repository**
   ```powershell
   cd "C:\Users\<YourUser>\OneDrive\Desktop\AI Cyber-Security System"
   ```

2. **Activate virtual environment**
   ```powershell
   .\div\Scripts\Activate.ps1
   ```

3. **Install dependencies** (if needed)
   ```powershell
   pip install -r requirements.txt
   ```

4. **Start the system**
   ```powershell
   .\run.bat
   ```
   This will:
   - Auto-heal missing packages
   - Start FastAPI backend on `http://localhost:8000`
   - Start Streamlit dashboard on `http://localhost:8501`

5. **Access the dashboard**
   Open browser → `http://localhost:8501`

---

## 🚀 Usage

### Via Dashboard (Recommended)

1. **File Scanning**
   - Upload a file in "File & URL Scanner" tab
   - System returns: BLOCKED/SUSPICIOUS/ALLOWED with detailed indicators
   - View Model Score, Rule Score, and risk factors

2. **URL Scanning**
   - Paste URL and submit
   - Get decision badge + visual indicator breakdown
   - See individual rule scores contributing to decision

3. **Communications Analysis**
   - Paste text/email content
   - Detects keywords, misspelled words, embedded threats
   - Color-coded risk indicators

4. **System Statistics**
   - View total scans processed
   - Threat history with timestamps
   - Real-time system health

### Via API

```bash
# Scan URL
curl -X POST http://localhost:8000/scan-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Scan File (multipart)
curl -X POST http://localhost:8000/scan-file \
  -F "file=@/path/to/file"

# Analyze Text
curl -X POST http://localhost:8000/analyze-text \
  -H "Content-Type: application/json" \
  -d '{"text": "sample message"}'

# Health Check
curl http://localhost:8000/health

# System Stats
curl http://localhost:8000/stats
```

---

## 📡 API Documentation

### Endpoints

| Endpoint | Method | Input | Output |
|----------|--------|-------|--------|
| `/scan-url` | POST | `{"url": "..."}` | Decision + indicators |
| `/scan-file` | POST | multipart file | Decision + indicators |
| `/analyze-text` | POST | `{"text": "..."}` | Keywords + misspellings |
| `/health` | GET | - | `{"status": "ok"}` |
| `/stats` | GET | - | Scan metrics |

### Response Format

```json
{
  "decision": "BLOCKED",
  "score": 0.75,
  "model_score": 0.68,
  "rule_score": 0.82,
  "blocked": true,
  "indicators": [
    "IP address detected",
    "HTTP instead of HTTPS",
    "Suspicious keyword"
  ],
  "timestamp": "2024-05-17T10:30:45Z"
}
```

---

## 🎨 Dashboard Features

### Visual Design
- **Gradient Card Backgrounds**: Modern purple-blue gradients
- **Decision Badges**: BLOCKED (red), SUSPICIOUS (amber), ALLOWED (green)
- **Indicator Chips**: Color-coded risk factors and keywords
- **Responsive Layout**: Works on desktop and tablet
- **Custom Font**: Space Grotesk for modern typography

### Tabs

1. **File & URL Scanner**
   - Single interface for both file and URL analysis
   - Real-time results with visual decision banner
   - Detailed score breakdown and risk factors

2. **Communications Analyzer**
   - Text/email threat analysis
   - Keyword highlighting (yellow chips)
   - Misspelling detection (red chips)
   - Embedded URL scanning

3. **System Stats**
   - Total scans processed
   - Threat distribution
   - System health status
   - Threat timeline

---

## 🤖 Models

### Malware Detector
- **Type**: RandomForest/HistGradientBoosting Ensemble
- **Input**: File byte histogram (256 bins) + heuristics
- **Target Accuracy**: 90%+
- **Output**: Probability (0-1)
- **Fallback**: Entropy + MZ header + suspicious strings detection

**Model File**: `sentinel_ai/models/models_store/malware_clf.joblib`

### Phishing Detector
- **Type**: Transformer embeddings (DistilBERT) + RandomForest
- **Input**: URL text embeddings
- **Output**: Probability (0-1)
- **Fallback**: HTTPS check, IP detection, domain analysis, keyword matching

**Model File**: `sentinel_ai/models/models_store/phishing_clf.joblib`

### Training

**Retrain Malware Model:**
```powershell
.\div\Scripts\python.exe sentinel_ai\training\train_malware.py
```

**Retrain Phishing Model:**
```powershell
.\div\Scripts\python.exe sentinel_ai\training\train_phishing.py
```

Models automatically save to `sentinel_ai/models/models_store/`

---

## 📁 Project Structure

```
AI Cyber-Security System/
├── sentinel_ai/
│   ├── models/
│   │   ├── models_store/              # Trained models (joblib format)
│   │   │   ├── malware_clf.joblib
│   │   │   ├── phishing_clf.joblib
│   │   │   └── malware_automl_model.pkl
│   │   ├── malware_model.py           # Malware detection class
│   │   └── phishing_model.py          # Phishing detection class
│   ├── prevention/
│   │   └── scanner.py                 # Core threat detection logic
│   ├── api/
│   │   └── server.py                  # FastAPI endpoints
│   ├── ui/
│   │   └── dashboard.py               # Streamlit interface
│   ├── training/
│   │   ├── train_malware.py           # Malware model training
│   │   └── train_phishing.py          # Phishing model training
│   └── utils/
│       └── self_heal.py               # Auto-package installer
├── datasets/
│   ├── train.csv                      # Malware training data (20K rows)
│   └── phishing/
│       └── Phishing_Legitimate_full.csv
├── run.bat                            # System startup script
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

---

## 🔧 Tech Stack

### Backend
- **Framework**: FastAPI + Uvicorn
- **Language**: Python 3.11
- **ML/Data**: scikit-learn, NumPy, Pandas
- **NLP**: Transformers (DistilBERT), sentence-transformers

### Frontend
- **Framework**: Streamlit
- **Styling**: Custom CSS with gradients
- **Assets**: Space Grotesk font

### ML/AI
- **Models**: RandomForest, HistGradientBoosting
- **Hyperparameter Tuning**: RandomizedSearchCV
- **Serialization**: Joblib
- **Feature Engineering**: Byte histograms, embeddings

### Development Tools
- Virtual Environment: venv (Python 3.11)
- Package Manager: pip
- Version Control: Git-ready

---

## 📊 Performance Metrics

- **Response Time**: <500ms per scan
- **Malware Accuracy Target**: 90%+
- **Phishing Detection Precision**: High (minimizes false positives)
- **System Uptime**: 24/7 with auto-recovery
- **Scalability**: Concurrent API requests supported

---

## 🔒 Security Best Practices

1. **Sandboxed File Analysis**: Files analyzed in-memory, no execution
2. **HTTPS Validation**: Prefers encrypted connections
3. **Heuristic Redundancy**: Multiple detection layers prevent bypasses
4. **Audit Logging**: All scans timestamped and recorded
5. **Safety-First Defaults**: Uncertain cases marked SUSPICIOUS/BLOCKED

---

## 📝 License & Credits

Enterprise prototype developed for advanced cyber-security monitoring.

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 already in use | Kill old process: `Get-Process \| Where-Object {$_.Port -eq 8000}` |
| Models not loading | Run trainers to regenerate: `train_malware.py`, `train_phishing.py` |
| Stale Streamlit cache | Hard refresh: `Ctrl+F5` |
| Missing packages | Auto-installed by `self_heal.py` on startup |
| Transformer hang | Uses spec-checking (no import), lightweight loading |

---

## 🚀 Future Enhancements

- [ ] Deep learning model (CNN for file analysis)
- [ ] Behavior-based anomaly detection
- [ ] Threat intelligence feed integration
- [ ] Multi-language support
- [ ] Docker containerization
- [ ] Database persistence layer
- [ ] Webhook notifications
- [ ] Advanced threat analytics

---

**Last Updated**: May 17, 2026  
**Status**: Production Ready ✅
