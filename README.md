# 🤖 Argus - AI-Powered Predictive Monitoring Platform

<img src="https://img.shields.io/badge/AI-GPT%205.2-blue" /> <img src="https://img.shields.io/badge/Backend-FastAPI-green" /> <img src="https://img.shields.io/badge/Frontend-React-cyan" /> <img src="https://img.shields.io/badge/Database-MongoDB-green" />

**Argus** is an intelligent monitoring platform that predicts system failures **before they happen**. Instead of only tracking metrics after problems occur, Argus analyzes patterns in logs, performance data, and system behavior to flag potential issues **hours in advance** using AI-powered analysis.

---

# ✨ Features

## 🎯 Core Features

- **Predictive Monitoring** – Detect potential system failures before they occur
- **Infrastructure Monitoring** – Real-time tracking of CPU, memory, disk, and network metrics
- **Application Monitoring** – Service latency, error rates, and request throughput analysis
- **AI-Powered Predictions** – Trend-based failure predictions with confidence scoring
- **Smart Alerting System** – Severity-based alerts with AI root cause analysis
- **Incident Management** – Track incidents from detection to resolution
- **Log Explorer** – Full-text log search with filtering and real-time streaming
- **Visual Dashboard** – Interactive charts and monitoring insights

---

# 🔍 What It Monitors

### Infrastructure
- CPU utilization
- Memory usage
- Disk usage
- Network I/O
- Server uptime

### Applications
- Service latency percentiles (P50, P95, P99)
- Request throughput
- Error rates
- Success rates

### AI Predictions
- Trend-based anomaly detection
- Time-to-threshold breach estimation
- Confidence scoring
- AI-powered prevention plans

---

# 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Argus Monitoring System                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────┐    │
│   │   Frontend   │◄───►│   Backend    │◄───►│ MongoDB  │    │
│   │   (React)    │     │  (FastAPI)   │     │          │    │
│   └──────────────┘     └──────┬───────┘     └──────────┘    │
│                                │                             │
│                        ┌───────┴────────┐                    │
│                        │                │                    │
│                 ┌──────▼─────┐   ┌─────▼──────┐             │
│                 │ Prediction │   │  Anomaly   │             │
│                 │  Engine    │   │ Detection  │             │
│                 └────────────┘   └────────────┘             │
│                                │                             │
│                                ▼                             │
│                        ┌──────────────────┐                  │
│                        │ OpenAI GPT-5.2   │                  │
│                        └──────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

---

# 🚀 Quick Start

## Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB
- Yarn package manager

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd argus
```

### 2. Setup Backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Setup Frontend

```bash
cd frontend
yarn install
```

### 4. Configure Environment Variables

Backend (`/backend/.env`)

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=argus_monitoring
EMERGENT_LLM_KEY=<your-key>
```

Frontend (`/frontend/.env`)

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 5. Run the Application

```bash
# Terminal 1 - Backend
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend
cd frontend
yarn start
```

### 6. Access the Application

- **Frontend**: http://localhost:3000  
- **Backend API Docs**: http://localhost:8001/docs  

---

# 📖 Usage

## Dashboard Monitoring

The dashboard provides a real-time overview of system health including:

- Total services monitored
- Healthy vs unhealthy services
- Active anomalies
- Failure predictions
- Latency and error trends

---

## Infrastructure Monitoring

Track server performance metrics including:

- CPU usage
- Memory utilization
- Disk consumption
- Health status indicators (healthy, warning, critical)

---

## Application Monitoring

Monitor application performance metrics such as:

- Latency percentiles (P50, P95, P99)
- Error rate tracking
- Request throughput
- Success rate

---

## AI-Powered Analysis

AI explanations provide:

- **Root Cause Analysis** – Identify the most likely cause
- **Immediate Actions** – Recommended steps to resolve the issue
- **Long-Term Fix** – Prevent recurrence
- **Time to Impact** – Estimated timeline if unresolved

---

# 🛠️ API Endpoints

## Core Endpoints

```bash
GET /api/health
GET /api/dashboard/overview
GET /api/infrastructure/servers
GET /api/applications/services
```

---

## Data Ingestion

```bash
POST /api/metrics
POST /api/metrics/bulk
POST /api/logs
```

---

## Monitoring

```bash
GET /api/alerts
GET /api/predictions
GET /api/anomalies
GET /api/incidents
GET /api/logs
```

---

## AI Analysis

```bash
POST /api/anomalies/explain
POST /api/predictions/explain
GET /api/incidents/{id}/analyze
```

---

# 📊 Dashboard Metrics

Argus tracks multiple monitoring metrics:

- **Total Services**
- **Healthy Services**
- **Active Alerts**
- **Predicted Failures**
- **Latency Trends**
- **Error Rate Trends**

---

# 🎨 Tech Stack

### Backend

- FastAPI  
- MongoDB  
- OpenAI GPT-5.2  
- Uvicorn  

### Frontend

- React 18  
- Tailwind CSS  
- Recharts  
- Lucide React  

---

# 📁 Project Structure

```
argus/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   └── .env
│
├── docs/
│   └── screenshots/
│
└── README.md
```

---

# 🤝 Contributing

1. Fork the repository  
2. Create your feature branch (`git checkout -b feature/amazing-feature`)  
3. Commit your changes (`git commit -m 'Add amazing feature'`)  
4. Push to the branch (`git push origin feature/amazing-feature`)  
5. Open a Pull Request  

---

# 📄 License

MIT License

---

# 🎯 Business Impact

Argus helps engineering teams:

- **Prevent downtime** with predictive alerts
- **Reduce MTTR** using AI root cause analysis
- **Improve reliability** with proactive monitoring
- **Centralize observability** across infrastructure and applications
- **Make data-driven decisions** about system health

---

# 🔗 Acknowledgments

- OpenAI for GPT-5.2 API  
- Recharts for visualization  
- Tailwind CSS for styling  
- Lucide Icons  


