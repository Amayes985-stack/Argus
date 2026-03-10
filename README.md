# Argus - AI-Powered Predictive Monitoring Platform

Argus is an intelligent monitoring platform that uses AI to predict system failures before they happen. Instead of just tracking metrics after problems occur, Argus analyzes patterns in logs, performance data, and system behavior to flag potential issues hours in advance.

---

## Features

### 🖥️ Infrastructure Monitoring
- Real-time server metrics (CPU, memory, disk usage)
- Health status indicators (healthy, warning, critical)
- Network I/O tracking
- Uptime monitoring

### 📊 Application Monitoring
- Service latency percentiles (P50, P95, P99)
- Error rate tracking
- Request throughput metrics
- Success rate monitoring

### 🔮 AI-Powered Predictions
- Trend-based failure predictions
- Time-to-breach estimates
- Confidence scoring
- GPT-5.2 powered prevention plans

### 🚨 Smart Alerting
- Severity-based alerts (low, medium, high, critical)
- AI-generated root cause analysis
- Actionable recommendations
- Alert lifecycle management

### 📋 Incident Management
- Incident timeline tracking
- Status progression (investigating → identified → monitoring → resolved)
- Root cause documentation
- AI-powered incident analysis

### 📝 Log Explorer
- Full-text search
- Service and level filtering
- Color-coded log entries
- Real-time log streaming

---

## Screenshots

### Dashboard
Real-time system overview with service health cards, latency charts, and anomaly distribution.
- Key metrics: Total Services, Healthy Services, Active Anomalies, Predictions
- Service Health grid showing latency and error rates per service
- API Gateway Latency chart (6h time series)
- Anomalies by Severity bar chart

### Infrastructure Monitoring
Server cards displaying CPU, memory, and disk metrics with visual progress bars.
- Server status badges (healthy/warning/critical)
- Color-coded progress bars for resource utilization
- Real-time metric updates

### Application Monitoring  
Service metrics with latency percentiles (P50/P95/P99), error rates, and request throughput.
- Per-service health status
- Success rate tracking
- Request count per minute

### Alerts
Severity-based alerts with status tracking and AI-powered explanations.
- Severity badges (low/medium/high/critical)
- Status indicators (active/acknowledged/resolved)
- "AI Explain" button for each alert

### AI-Powered Analysis
GPT-5.2 powered modal providing:
- **Root Cause**: Detailed analysis of what likely caused the issue
- **Immediate Action**: Steps to take right now
- **Long Term Fix**: Recommendations for preventing recurrence
- **Time to Impact**: Estimated timeline if not addressed

### Failure Predictions
AI-powered predictions with:
- Current vs Predicted values
- Time to threshold breach
- Confidence percentage
- "Get AI Prevention Plan" button

### Incident Timeline
Track incidents from detection to resolution:
- Severity and status badges
- Root cause documentation
- AI Analysis for each incident

### Log Explorer
Search and filter logs with:
- Full-text search
- Service dropdown filter
- Level filter (INFO/WARN/ERROR/CRITICAL)
- Color-coded log entries

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Tailwind CSS, Recharts |
| Backend | FastAPI (Python) |
| Database | MongoDB |
| AI | OpenAI GPT-5.2 |

---

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- MongoDB

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd argus
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   yarn install
   ```

4. **Environment Variables**

   Backend (`/backend/.env`):
   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=argus_monitoring
   EMERGENT_LLM_KEY=<your-key>
   ```

   Frontend (`/frontend/.env`):
   ```env
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

5. **Run the Application**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload

   # Terminal 2 - Frontend
   cd frontend
   yarn start
   ```

6. **Access the Application**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8001/docs

---

## API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/dashboard/overview` | GET | Dashboard summary with service health |
| `/api/infrastructure/servers` | GET | Server metrics (CPU, memory, disk) |
| `/api/applications/services` | GET | Application service metrics |

### Data Ingestion

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/metrics` | POST | Ingest single metric |
| `/api/metrics/bulk` | POST | Ingest multiple metrics |
| `/api/logs` | POST | Ingest log entry |

### Monitoring

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/alerts` | GET | List all alerts |
| `/api/predictions` | GET | Get failure predictions |
| `/api/anomalies` | GET | Get detected anomalies |
| `/api/incidents` | GET | Get incident timeline |
| `/api/logs` | GET | Search and filter logs |

### AI Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/anomalies/explain` | POST | AI explanation for anomaly |
| `/api/predictions/explain` | POST | AI prevention plan for prediction |
| `/api/incidents/{id}/analyze` | GET | AI analysis for incident |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │Dashboard│ │ Infra   │ │  Apps   │ │ Alerts  │  ...      │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │
└───────┼───────────┼───────────┼───────────┼─────────────────┘
        │           │           │           │
        ▼           ▼           ▼           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Anomaly    │  │  Prediction  │  │     AI       │      │
│  │  Detection   │  │   Engine     │  │ Explanation  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ MongoDB │        │ OpenAI  │        │ Metrics │
   │         │        │ GPT-5.2 │        │ Store   │
   └─────────┘        └─────────┘        └─────────┘
```

---

## Project Structure

```
argus/
├── backend/
│   ├── server.py          # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Backend environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   ├── index.js      # Entry point
│   │   └── index.css     # Global styles
│   ├── public/
│   │   └── index.html    # HTML template
│   ├── package.json      # Node dependencies
│   └── .env             # Frontend environment variables
├── docs/
│   └── screenshots/      # Application screenshots
└── README.md
```

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- [OpenAI](https://openai.com) for GPT-5.2 API
- [Recharts](https://recharts.org) for data visualization
- [Tailwind CSS](https://tailwindcss.com) for styling
- [Lucide](https://lucide.dev) for icons
