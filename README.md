# Argus - AI-Powered Predictive Monitoring Platform

Argus is an intelligent monitoring platform that uses AI to predict system failures before they happen. Instead of just tracking metrics after problems occur, Argus analyzes patterns in logs, performance data, and system behavior to flag potential issues hours in advance.

![Argus Dashboard](https://images.unsplash.com/photo-1764258560300-2346b28b4e7c?w=800)

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

## Tech Stack

- **Frontend**: React 18, Tailwind CSS, Recharts
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **AI**: OpenAI GPT-5.2

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
   ```
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=argus_monitoring
   EMERGENT_LLM_KEY=<your-key>
   ```

   Frontend (`/frontend/.env`):
   ```
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

5. **Run the Application**
   ```bash
   # Backend
   cd backend
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload

   # Frontend
   cd frontend
   yarn start
   ```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/dashboard/overview` | GET | Dashboard summary |
| `/api/infrastructure/servers` | GET | Server metrics |
| `/api/applications/services` | GET | Service metrics |
| `/api/metrics` | GET/POST | Metrics ingestion |
| `/api/alerts` | GET/POST | Alert management |
| `/api/predictions` | GET | Failure predictions |
| `/api/anomalies` | GET | Detected anomalies |
| `/api/incidents` | GET/POST | Incident management |
| `/api/logs` | GET/POST | Log management |
| `/api/anomalies/explain` | POST | AI anomaly analysis |
| `/api/predictions/explain` | POST | AI prediction analysis |

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

## Screenshots

### Dashboard
Real-time system overview with service health, latency charts, and anomaly distribution.

### Infrastructure Monitoring
Server cards displaying CPU, memory, and disk metrics with visual progress bars.

### AI Explanations
GPT-5.2 powered analysis providing root cause, immediate actions, and long-term fixes.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- OpenAI for GPT-5.2 API
- Recharts for data visualization
- Tailwind CSS for styling
