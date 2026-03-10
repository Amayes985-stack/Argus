# Sentinels - AI-Powered Predictive Monitoring Platform

## Original Problem Statement
Build an AI-powered monitoring platform that uses AI to predict system failures before they happen. Instead of just tracking metrics after problems occur, the system would analyze patterns in logs, performance data, and user behavior to flag potential issues hours or days in advance.

## User Choices
- **Monitoring Scope**: Both infrastructure + application monitoring
- **AI Approach**: Hybrid (custom anomaly detection + LLM for explanations)
- **Data Sources**: Both demo data + real ingestion capability
- **Features**: All - real-time dashboards, alerting, predictions, incidents, logs

## Architecture

### Tech Stack
- **Frontend**: React 18 + Tailwind CSS + Recharts
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **AI**: OpenAI GPT-5.2 via emergentintegrations library

### Key Components
1. **Anomaly Detection Engine**: Statistical z-score based detection + threshold-based
2. **Prediction Engine**: Trend analysis for predicting future breaches
3. **AI Explanation Service**: GPT-5.2 powered analysis with actionable recommendations
4. **Real-time Dashboard**: Service health, charts, metrics

## User Personas
- **DevOps Engineers**: Monitor infrastructure health, respond to alerts
- **SREs**: Analyze incidents, implement long-term fixes
- **Engineering Leads**: Review system health, track incidents

## Core Requirements (Static)
- [x] Real-time dashboard with system overview
- [x] Infrastructure monitoring (servers, CPU, memory, disk)
- [x] Application monitoring (services, latency, error rates)
- [x] Alerting system with severity levels
- [x] AI-powered predictions for future issues
- [x] Incident timeline with root cause tracking
- [x] Log explorer with search and filters
- [x] AI explanations for anomalies and predictions

## What's Been Implemented (March 10, 2026)

### Backend APIs
- `/api/health` - Health check
- `/api/dashboard/overview` - Aggregated dashboard data
- `/api/infrastructure/servers` - Server metrics
- `/api/applications/services` - Application service metrics
- `/api/metrics` - Metrics ingestion and retrieval
- `/api/logs` - Log management with filtering
- `/api/anomalies` - Anomaly detection
- `/api/predictions` - Failure predictions
- `/api/alerts` - Alert management
- `/api/incidents` - Incident timeline
- `/api/*/explain` - AI-powered explanations

### Frontend Views
- Dashboard (service health, charts, metrics overview)
- Infrastructure (server cards with CPU/memory/disk)
- Applications (service latency percentiles, error rates)
- Alerts (severity badges, status, AI explanation modal)
- Predictions (failure forecasts with AI prevention plans)
- Incidents (timeline with root cause, AI analysis)
- Logs (explorer with search, service/level filters)

### AI Features
- Alert analysis with root cause, immediate action, long-term fix
- Prediction explanations with prevention steps and business impact
- Incident analysis with similar incident patterns

## Prioritized Backlog

### P0 (Critical) - COMPLETED
- [x] Core monitoring dashboard
- [x] AI anomaly explanations
- [x] Real-time data visualization

### P1 (High Priority) - Future
- [ ] Email/Slack notifications for critical alerts
- [ ] Custom alert threshold configuration UI
- [ ] Historical data retention and analysis
- [ ] User authentication and team management

### P2 (Medium Priority) - Future
- [ ] Webhooks for real-time metric ingestion
- [ ] Custom dashboard layouts
- [ ] SLA/SLO tracking
- [ ] Runbook automation integration

### P3 (Nice to Have)
- [ ] Mobile-responsive design improvements
- [ ] Dark/light theme toggle
- [ ] Export reports as PDF
- [ ] Integration with PagerDuty/Opsgenie

## Next Tasks
1. Add notification integrations (Slack, Email)
2. Implement user authentication
3. Add custom alert configuration UI
4. Implement historical data retention
