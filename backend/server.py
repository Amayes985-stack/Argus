"""
Sentinels - AI-Powered Predictive Monitoring Platform
Backend Server with Anomaly Detection, Predictions & AI Explanations
"""

import os
import random
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient
import numpy as np
from sklearn.ensemble import IsolationForest
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Initialize FastAPI
app = FastAPI(title="Sentinels Monitoring API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "sentinels_monitoring")
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
metrics_collection = db["metrics"]
logs_collection = db["logs"]
alerts_collection = db["alerts"]
incidents_collection = db["incidents"]
predictions_collection = db["predictions"]

# Ensure indexes
metrics_collection.create_index([("timestamp", -1)])
logs_collection.create_index([("timestamp", -1)])
alerts_collection.create_index([("created_at", -1)])
predictions_collection.create_index([("predicted_at", -1)])

# ===================== PYDANTIC MODELS =====================

class MetricData(BaseModel):
    service: str
    metric_type: str  # cpu, memory, disk, network, latency, error_rate, request_count
    value: float
    unit: str
    host: Optional[str] = None
    timestamp: Optional[str] = None

class LogEntry(BaseModel):
    service: str
    level: str  # info, warn, error, critical
    message: str
    host: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[dict] = None

class AlertConfig(BaseModel):
    metric_type: str
    threshold: float
    condition: str  # above, below
    severity: str  # low, medium, high, critical

class IncidentUpdate(BaseModel):
    status: str  # investigating, identified, monitoring, resolved
    notes: Optional[str] = None

# ===================== DEMO DATA GENERATION =====================

SERVICES = ["api-gateway", "user-service", "payment-service", "inventory-service", "notification-service"]
HOSTS = ["prod-server-1", "prod-server-2", "prod-server-3", "db-primary", "db-replica", "cache-server"]

def generate_base_metrics():
    """Generate realistic base metrics with patterns"""
    return {
        "cpu": random.gauss(45, 15),
        "memory": random.gauss(60, 10),
        "disk": random.gauss(55, 8),
        "network_in": random.gauss(500, 100),
        "network_out": random.gauss(300, 80),
        "latency": random.gauss(120, 40),
        "error_rate": max(0, random.gauss(0.5, 0.3)),
        "request_count": random.gauss(1000, 200)
    }

def inject_anomaly(metrics: dict, anomaly_type: str) -> dict:
    """Inject realistic anomalies into metrics"""
    if anomaly_type == "cpu_spike":
        metrics["cpu"] = random.uniform(85, 99)
    elif anomaly_type == "memory_leak":
        metrics["memory"] = random.uniform(88, 98)
    elif anomaly_type == "latency_degradation":
        metrics["latency"] = random.uniform(800, 2000)
    elif anomaly_type == "error_surge":
        metrics["error_rate"] = random.uniform(5, 25)
    elif anomaly_type == "disk_full":
        metrics["disk"] = random.uniform(90, 98)
    return metrics

def generate_historical_metrics(hours: int = 24):
    """Generate historical metrics data"""
    data = []
    now = datetime.now(timezone.utc)
    
    for i in range(hours * 12):  # 5-minute intervals
        timestamp = now - timedelta(minutes=i * 5)
        for service in SERVICES:
            metrics = generate_base_metrics()
            
            # Inject occasional anomalies (10% chance)
            if random.random() < 0.1:
                anomaly = random.choice(["cpu_spike", "memory_leak", "latency_degradation", "error_surge"])
                metrics = inject_anomaly(metrics, anomaly)
            
            for metric_type, value in metrics.items():
                data.append({
                    "service": service,
                    "metric_type": metric_type,
                    "value": round(value, 2),
                    "unit": get_unit(metric_type),
                    "host": random.choice(HOSTS),
                    "timestamp": timestamp.isoformat()
                })
    return data

def get_unit(metric_type: str) -> str:
    units = {
        "cpu": "%", "memory": "%", "disk": "%",
        "network_in": "MB/s", "network_out": "MB/s",
        "latency": "ms", "error_rate": "%", "request_count": "req/min"
    }
    return units.get(metric_type, "")

def generate_logs(count: int = 100):
    """Generate sample log entries"""
    log_templates = {
        "info": [
            "Request processed successfully for {service}",
            "Connection established to {service}",
            "Cache refreshed for {service}",
            "Health check passed for {service}"
        ],
        "warn": [
            "High latency detected in {service}: {value}ms",
            "Memory usage above 80% in {service}",
            "Connection pool nearing limit for {service}",
            "Retry attempt {value} for {service}"
        ],
        "error": [
            "Failed to connect to {service}: timeout after {value}ms",
            "Database query failed in {service}",
            "Authentication failure in {service}",
            "Rate limit exceeded for {service}"
        ],
        "critical": [
            "Service {service} is unresponsive",
            "Database connection lost for {service}",
            "Memory exhaustion in {service}",
            "Disk space critical for {service}"
        ]
    }
    
    logs = []
    now = datetime.now(timezone.utc)
    
    for i in range(count):
        level = random.choices(["info", "warn", "error", "critical"], weights=[70, 15, 10, 5])[0]
        service = random.choice(SERVICES)
        template = random.choice(log_templates[level])
        
        logs.append({
            "log_id": str(uuid.uuid4()),
            "service": service,
            "level": level,
            "message": template.format(service=service, value=random.randint(100, 5000)),
            "host": random.choice(HOSTS),
            "timestamp": (now - timedelta(minutes=random.randint(0, 60*24))).isoformat(),
            "metadata": {"request_id": str(uuid.uuid4())[:8]}
        })
    return logs

# ===================== ANOMALY DETECTION =====================

class AnomalyDetector:
    def __init__(self):
        self.models = {}
        self.thresholds = {
            "cpu": 85, "memory": 90, "disk": 90,
            "latency": 500, "error_rate": 5
        }
    
    def detect_anomalies(self, metrics: List[dict]) -> List[dict]:
        """Detect anomalies using Isolation Forest and threshold-based detection"""
        anomalies = []
        
        # Group by service and metric_type
        grouped = {}
        for m in metrics:
            key = (m["service"], m["metric_type"])
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(m)
        
        for (service, metric_type), data in grouped.items():
            values = np.array([d["value"] for d in data]).reshape(-1, 1)
            
            if len(values) < 10:
                continue
            
            # Isolation Forest for ML-based detection
            model = IsolationForest(contamination=0.1, random_state=42)
            predictions = model.fit_predict(values)
            
            for i, pred in enumerate(predictions):
                if pred == -1:  # Anomaly
                    anomalies.append({
                        "service": service,
                        "metric_type": metric_type,
                        "value": data[i]["value"],
                        "timestamp": data[i]["timestamp"],
                        "detection_method": "isolation_forest",
                        "severity": self._calculate_severity(metric_type, data[i]["value"])
                    })
            
            # Threshold-based detection
            if metric_type in self.thresholds:
                for d in data:
                    if d["value"] > self.thresholds[metric_type]:
                        if not any(a["timestamp"] == d["timestamp"] and a["service"] == service for a in anomalies):
                            anomalies.append({
                                "service": service,
                                "metric_type": metric_type,
                                "value": d["value"],
                                "timestamp": d["timestamp"],
                                "detection_method": "threshold",
                                "severity": self._calculate_severity(metric_type, d["value"])
                            })
        
        return anomalies
    
    def _calculate_severity(self, metric_type: str, value: float) -> str:
        thresholds = {
            "cpu": [(95, "critical"), (85, "high"), (75, "medium")],
            "memory": [(95, "critical"), (90, "high"), (80, "medium")],
            "disk": [(95, "critical"), (90, "high"), (85, "medium")],
            "latency": [(2000, "critical"), (1000, "high"), (500, "medium")],
            "error_rate": [(20, "critical"), (10, "high"), (5, "medium")]
        }
        
        if metric_type in thresholds:
            for threshold, severity in thresholds[metric_type]:
                if value >= threshold:
                    return severity
        return "low"

detector = AnomalyDetector()

# ===================== PREDICTION ENGINE =====================

class PredictionEngine:
    def predict_future_issues(self, metrics: List[dict], hours_ahead: int = 6) -> List[dict]:
        """Predict potential future issues based on trends"""
        predictions = []
        
        # Group by service and metric_type
        grouped = {}
        for m in metrics:
            key = (m["service"], m["metric_type"])
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(m)
        
        for (service, metric_type), data in grouped.items():
            if len(data) < 20:
                continue
            
            # Sort by timestamp and get values
            sorted_data = sorted(data, key=lambda x: x["timestamp"])
            values = [d["value"] for d in sorted_data[-20:]]
            
            # Calculate trend
            if len(values) >= 5:
                recent_avg = np.mean(values[-5:])
                older_avg = np.mean(values[:5])
                trend = (recent_avg - older_avg) / max(older_avg, 1)
                
                # Predict future value
                predicted_value = recent_avg * (1 + trend * hours_ahead)
                
                # Generate prediction if concerning
                thresholds = {"cpu": 85, "memory": 90, "disk": 90, "latency": 500, "error_rate": 5}
                
                if metric_type in thresholds and predicted_value > thresholds[metric_type]:
                    confidence = min(95, 60 + abs(trend) * 100)
                    
                    predictions.append({
                        "prediction_id": str(uuid.uuid4()),
                        "service": service,
                        "metric_type": metric_type,
                        "current_value": round(recent_avg, 2),
                        "predicted_value": round(predicted_value, 2),
                        "threshold": thresholds[metric_type],
                        "hours_until_breach": round(hours_ahead * (1 - recent_avg / predicted_value), 1),
                        "confidence": round(confidence, 1),
                        "trend": "increasing" if trend > 0 else "decreasing",
                        "predicted_at": datetime.now(timezone.utc).isoformat()
                    })
        
        return predictions

prediction_engine = PredictionEngine()

# ===================== AI EXPLANATION ENGINE =====================

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")

async def generate_ai_explanation(anomaly: dict) -> dict:
    """Generate AI-powered explanation and recommendations for an anomaly"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"anomaly-{anomaly.get('service', 'unknown')}-{uuid.uuid4().hex[:8]}",
            system_message="""You are an expert DevOps engineer and SRE specialist. 
            Analyze system anomalies and provide clear, actionable insights.
            Be concise but thorough. Focus on root cause analysis and immediate actions."""
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"""Analyze this system anomaly and provide insights:

Service: {anomaly.get('service', 'Unknown')}
Metric: {anomaly.get('metric_type', 'Unknown')}
Current Value: {anomaly.get('value', 'N/A')}
Severity: {anomaly.get('severity', 'Unknown')}
Detection Method: {anomaly.get('detection_method', 'threshold')}

Provide:
1. Likely root cause (2-3 sentences)
2. Immediate action to take (1-2 steps)
3. Long-term fix recommendation
4. Estimated time to resolution if not addressed

Format as JSON with keys: root_cause, immediate_action, long_term_fix, time_to_impact"""

        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse response
        import json
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            
            explanation = json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError):
            explanation = {
                "root_cause": response[:200] if len(response) > 200 else response,
                "immediate_action": "Investigate the affected service and review recent changes",
                "long_term_fix": "Implement proper monitoring and alerting thresholds",
                "time_to_impact": "Within 1-2 hours if not addressed"
            }
        
        return {
            "anomaly": anomaly,
            "explanation": explanation,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "anomaly": anomaly,
            "explanation": {
                "root_cause": f"AI analysis unavailable: {str(e)}",
                "immediate_action": "Manual investigation required",
                "long_term_fix": "Review system logs and metrics",
                "time_to_impact": "Unknown"
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

async def generate_prediction_explanation(prediction: dict) -> dict:
    """Generate AI explanation for a prediction"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"prediction-{prediction.get('service', 'unknown')}-{uuid.uuid4().hex[:8]}",
            system_message="""You are an expert SRE who predicts and prevents system failures.
            Provide actionable advice to prevent predicted issues. Be specific and practical."""
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"""A system issue is predicted. Analyze and provide prevention advice:

Service: {prediction.get('service', 'Unknown')}
Metric: {prediction.get('metric_type', 'Unknown')}
Current Value: {prediction.get('current_value', 'N/A')}
Predicted Value: {prediction.get('predicted_value', 'N/A')}
Threshold: {prediction.get('threshold', 'N/A')}
Hours Until Breach: {prediction.get('hours_until_breach', 'N/A')}
Confidence: {prediction.get('confidence', 'N/A')}%
Trend: {prediction.get('trend', 'Unknown')}

Provide:
1. What will likely happen if not addressed
2. Prevention steps (prioritized list of 3 actions)
3. Business impact if issue occurs
4. Recommended alert escalation

Format as JSON with keys: impact_prediction, prevention_steps, business_impact, escalation"""

        response = await chat.send_message(UserMessage(text=prompt))
        
        import json
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            explanation = json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError):
            explanation = {
                "impact_prediction": response[:200] if len(response) > 200 else response,
                "prevention_steps": ["Monitor the metric closely", "Prepare scaling resources", "Alert on-call team"],
                "business_impact": "Potential service degradation or outage",
                "escalation": "Notify engineering lead if trend continues"
            }
        
        return {
            "prediction": prediction,
            "explanation": explanation,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "prediction": prediction,
            "explanation": {
                "impact_prediction": f"AI analysis unavailable: {str(e)}",
                "prevention_steps": ["Manual review required"],
                "business_impact": "Unknown",
                "escalation": "Contact engineering team"
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

# ===================== API ENDPOINTS =====================

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# ----- Dashboard Overview -----

@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """Get aggregated dashboard overview"""
    now = datetime.now(timezone.utc)
    one_hour_ago = (now - timedelta(hours=1)).isoformat()
    
    # Get recent metrics
    recent_metrics = list(metrics_collection.find(
        {"timestamp": {"$gte": one_hour_ago}},
        {"_id": 0}
    ).sort("timestamp", -1).limit(500))
    
    # If no data, generate demo data
    if len(recent_metrics) < 50:
        demo_metrics = generate_historical_metrics(hours=2)
        metrics_collection.insert_many(demo_metrics)
        recent_metrics = demo_metrics[:500]
    
    # Calculate service health
    services_health = {}
    for service in SERVICES:
        service_metrics = [m for m in recent_metrics if m["service"] == service]
        if service_metrics:
            error_rate = np.mean([m["value"] for m in service_metrics if m["metric_type"] == "error_rate"]) if any(m["metric_type"] == "error_rate" for m in service_metrics) else 0
            latency = np.mean([m["value"] for m in service_metrics if m["metric_type"] == "latency"]) if any(m["metric_type"] == "latency" for m in service_metrics) else 0
            
            if error_rate > 10 or latency > 1000:
                status = "critical"
            elif error_rate > 5 or latency > 500:
                status = "warning"
            else:
                status = "healthy"
            
            services_health[service] = {
                "status": status,
                "error_rate": round(error_rate, 2),
                "avg_latency": round(latency, 2)
            }
    
    # Detect anomalies
    anomalies = detector.detect_anomalies(recent_metrics)
    
    # Get predictions
    predictions = prediction_engine.predict_future_issues(recent_metrics)
    
    # Active alerts count
    active_alerts = alerts_collection.count_documents({"status": {"$ne": "resolved"}})
    
    return {
        "services_health": services_health,
        "total_services": len(SERVICES),
        "healthy_services": len([s for s in services_health.values() if s["status"] == "healthy"]),
        "warning_services": len([s for s in services_health.values() if s["status"] == "warning"]),
        "critical_services": len([s for s in services_health.values() if s["status"] == "critical"]),
        "active_anomalies": len(anomalies),
        "active_predictions": len(predictions),
        "active_alerts": active_alerts,
        "last_updated": now.isoformat()
    }

# ----- Metrics -----

@app.post("/api/metrics")
async def ingest_metric(metric: MetricData):
    """Ingest a single metric"""
    data = metric.model_dump()
    data["timestamp"] = data["timestamp"] or datetime.now(timezone.utc).isoformat()
    metrics_collection.insert_one(data)
    return {"status": "ingested", "timestamp": data["timestamp"]}

@app.post("/api/metrics/bulk")
async def ingest_metrics_bulk(metrics: List[MetricData]):
    """Ingest multiple metrics"""
    data = []
    for m in metrics:
        d = m.model_dump()
        d["timestamp"] = d["timestamp"] or datetime.now(timezone.utc).isoformat()
        data.append(d)
    metrics_collection.insert_many(data)
    return {"status": "ingested", "count": len(data)}

@app.get("/api/metrics")
async def get_metrics(
    service: Optional[str] = None,
    metric_type: Optional[str] = None,
    hours: int = Query(default=1, ge=1, le=168)
):
    """Get metrics with optional filters"""
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    
    query = {"timestamp": {"$gte": since}}
    if service:
        query["service"] = service
    if metric_type:
        query["metric_type"] = metric_type
    
    metrics = list(metrics_collection.find(query, {"_id": 0}).sort("timestamp", -1).limit(1000))
    
    # Generate demo data if empty
    if not metrics:
        demo_data = generate_historical_metrics(hours=hours)
        filtered = [m for m in demo_data if (not service or m["service"] == service) and (not metric_type or m["metric_type"] == metric_type)]
        return {"metrics": filtered[:1000], "count": len(filtered[:1000])}
    
    return {"metrics": metrics, "count": len(metrics)}

@app.get("/api/metrics/timeseries")
async def get_metrics_timeseries(
    service: str,
    metric_type: str,
    hours: int = Query(default=6, ge=1, le=168)
):
    """Get time series data for charts"""
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    
    metrics = list(metrics_collection.find(
        {"service": service, "metric_type": metric_type, "timestamp": {"$gte": since}},
        {"_id": 0}
    ).sort("timestamp", 1).limit(500))
    
    # Generate demo if empty
    if not metrics:
        demo = generate_historical_metrics(hours=hours)
        metrics = [m for m in demo if m["service"] == service and m["metric_type"] == metric_type][:500]
    
    return {"service": service, "metric_type": metric_type, "data": metrics}

# ----- Infrastructure Monitoring -----

@app.get("/api/infrastructure/servers")
async def get_server_metrics():
    """Get current server infrastructure metrics"""
    now = datetime.now(timezone.utc)
    
    servers = []
    for host in HOSTS:
        metrics = generate_base_metrics()
        
        # Occasionally inject anomaly for demo
        if random.random() < 0.15:
            anomaly = random.choice(["cpu_spike", "memory_leak", "disk_full"])
            metrics = inject_anomaly(metrics, anomaly)
        
        status = "healthy"
        if metrics["cpu"] > 85 or metrics["memory"] > 90 or metrics["disk"] > 90:
            status = "critical"
        elif metrics["cpu"] > 70 or metrics["memory"] > 80 or metrics["disk"] > 80:
            status = "warning"
        
        servers.append({
            "host": host,
            "status": status,
            "cpu": round(metrics["cpu"], 1),
            "memory": round(metrics["memory"], 1),
            "disk": round(metrics["disk"], 1),
            "network_in": round(metrics["network_in"], 1),
            "network_out": round(metrics["network_out"], 1),
            "uptime": f"{random.randint(1, 90)} days",
            "last_updated": now.isoformat()
        })
    
    return {"servers": servers, "count": len(servers)}

# ----- Application Monitoring -----

@app.get("/api/applications/services")
async def get_application_services():
    """Get application service metrics"""
    now = datetime.now(timezone.utc)
    
    services = []
    for service in SERVICES:
        metrics = generate_base_metrics()
        
        if random.random() < 0.1:
            metrics = inject_anomaly(metrics, random.choice(["latency_degradation", "error_surge"]))
        
        status = "healthy"
        if metrics["error_rate"] > 10 or metrics["latency"] > 1000:
            status = "critical"
        elif metrics["error_rate"] > 5 or metrics["latency"] > 500:
            status = "warning"
        
        services.append({
            "service": service,
            "status": status,
            "latency_p50": round(metrics["latency"] * 0.7, 1),
            "latency_p95": round(metrics["latency"] * 1.2, 1),
            "latency_p99": round(metrics["latency"] * 1.5, 1),
            "error_rate": round(metrics["error_rate"], 2),
            "request_count": round(metrics["request_count"]),
            "success_rate": round(100 - metrics["error_rate"], 2),
            "last_updated": now.isoformat()
        })
    
    return {"services": services, "count": len(services)}

# ----- Logs -----

@app.post("/api/logs")
async def ingest_log(log: LogEntry):
    """Ingest a single log entry"""
    data = log.model_dump()
    data["log_id"] = str(uuid.uuid4())
    data["timestamp"] = data["timestamp"] or datetime.now(timezone.utc).isoformat()
    logs_collection.insert_one(data)
    return {"status": "ingested", "log_id": data["log_id"]}

@app.get("/api/logs")
async def get_logs(
    service: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=500)
):
    """Get logs with filters"""
    query = {}
    if service:
        query["service"] = service
    if level:
        query["level"] = level
    if search:
        query["message"] = {"$regex": search, "$options": "i"}
    
    logs = list(logs_collection.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit))
    
    # Generate demo if empty
    if not logs:
        demo_logs = generate_logs(limit)
        if service:
            demo_logs = [l for l in demo_logs if l["service"] == service]
        if level:
            demo_logs = [l for l in demo_logs if l["level"] == level]
        if search:
            demo_logs = [l for l in demo_logs if search.lower() in l["message"].lower()]
        return {"logs": demo_logs[:limit], "count": len(demo_logs[:limit])}
    
    return {"logs": logs, "count": len(logs)}

@app.get("/api/logs/stats")
async def get_log_stats():
    """Get log statistics"""
    demo_logs = generate_logs(500)
    
    stats = {
        "total": len(demo_logs),
        "by_level": {
            "info": len([l for l in demo_logs if l["level"] == "info"]),
            "warn": len([l for l in demo_logs if l["level"] == "warn"]),
            "error": len([l for l in demo_logs if l["level"] == "error"]),
            "critical": len([l for l in demo_logs if l["level"] == "critical"])
        },
        "by_service": {}
    }
    
    for service in SERVICES:
        stats["by_service"][service] = len([l for l in demo_logs if l["service"] == service])
    
    return stats

# ----- Anomaly Detection -----

@app.get("/api/anomalies")
async def get_anomalies(hours: int = Query(default=1, ge=1, le=24)):
    """Detect and return anomalies"""
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    
    metrics = list(metrics_collection.find(
        {"timestamp": {"$gte": since}},
        {"_id": 0}
    ).limit(1000))
    
    if len(metrics) < 50:
        metrics = generate_historical_metrics(hours=hours)
    
    anomalies = detector.detect_anomalies(metrics)
    
    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    anomalies.sort(key=lambda x: severity_order.get(x["severity"], 4))
    
    return {"anomalies": anomalies[:50], "count": len(anomalies)}

@app.get("/api/anomalies/{anomaly_id}/explain")
async def explain_anomaly(anomaly_id: str):
    """Get AI explanation for a specific anomaly"""
    # For demo, create a sample anomaly
    anomaly = {
        "service": random.choice(SERVICES),
        "metric_type": random.choice(["cpu", "memory", "latency", "error_rate"]),
        "value": random.uniform(80, 99),
        "severity": random.choice(["high", "critical"]),
        "detection_method": "isolation_forest"
    }
    
    explanation = await generate_ai_explanation(anomaly)
    return explanation

@app.post("/api/anomalies/explain")
async def explain_anomaly_custom(anomaly: dict):
    """Get AI explanation for provided anomaly data"""
    explanation = await generate_ai_explanation(anomaly)
    return explanation

# ----- Predictions -----

@app.get("/api/predictions")
async def get_predictions(hours_ahead: int = Query(default=6, ge=1, le=48)):
    """Get failure predictions"""
    metrics = list(metrics_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(500))
    
    if len(metrics) < 100:
        metrics = generate_historical_metrics(hours=24)
    
    predictions = prediction_engine.predict_future_issues(metrics, hours_ahead)
    
    # Sort by confidence
    predictions.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {"predictions": predictions[:20], "hours_ahead": hours_ahead}

@app.get("/api/predictions/{prediction_id}/explain")
async def explain_prediction(prediction_id: str):
    """Get AI explanation for a prediction"""
    # Create sample prediction for demo
    prediction = {
        "service": random.choice(SERVICES),
        "metric_type": random.choice(["cpu", "memory", "disk"]),
        "current_value": random.uniform(60, 80),
        "predicted_value": random.uniform(85, 98),
        "threshold": 85,
        "hours_until_breach": random.uniform(2, 8),
        "confidence": random.uniform(70, 95),
        "trend": "increasing"
    }
    
    explanation = await generate_prediction_explanation(prediction)
    return explanation

@app.post("/api/predictions/explain")
async def explain_prediction_custom(prediction: dict):
    """Get AI explanation for provided prediction"""
    explanation = await generate_prediction_explanation(prediction)
    return explanation

# ----- Alerts -----

@app.get("/api/alerts")
async def get_alerts(status: Optional[str] = None, severity: Optional[str] = None):
    """Get alerts"""
    query = {}
    if status:
        query["status"] = status
    if severity:
        query["severity"] = severity
    
    alerts = list(alerts_collection.find(query, {"_id": 0}).sort("created_at", -1).limit(100))
    
    # Generate demo alerts if empty
    if not alerts:
        demo_alerts = []
        for i in range(15):
            demo_alerts.append({
                "alert_id": str(uuid.uuid4()),
                "service": random.choice(SERVICES),
                "metric_type": random.choice(["cpu", "memory", "latency", "error_rate", "disk"]),
                "message": f"Alert: {random.choice(['High CPU usage', 'Memory leak detected', 'Latency spike', 'Error rate increase', 'Disk space low'])}",
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "status": random.choice(["active", "acknowledged", "resolved"]),
                "value": round(random.uniform(80, 99), 2),
                "threshold": round(random.uniform(70, 85), 2),
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=random.randint(5, 1440))).isoformat()
            })
        return {"alerts": demo_alerts, "count": len(demo_alerts)}
    
    return {"alerts": alerts, "count": len(alerts)}

@app.post("/api/alerts")
async def create_alert(alert: AlertConfig):
    """Create a new alert rule"""
    data = {
        "alert_id": str(uuid.uuid4()),
        **alert.model_dump(),
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    alerts_collection.insert_one(data)
    return {"status": "created", "alert_id": data["alert_id"]}

@app.patch("/api/alerts/{alert_id}")
async def update_alert(alert_id: str, status: str):
    """Update alert status"""
    result = alerts_collection.update_one(
        {"alert_id": alert_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "updated"}

# ----- Incidents -----

@app.get("/api/incidents")
async def get_incidents(status: Optional[str] = None):
    """Get incidents timeline"""
    query = {} if not status else {"status": status}
    
    incidents = list(incidents_collection.find(query, {"_id": 0}).sort("started_at", -1).limit(50))
    
    # Generate demo incidents if empty
    if not incidents:
        demo_incidents = []
        incident_types = [
            ("Database connection pool exhausted", "payment-service", "critical"),
            ("API gateway latency spike", "api-gateway", "high"),
            ("Memory leak in user service", "user-service", "medium"),
            ("Disk space warning on cache server", "cache-server", "low"),
            ("Network timeout to external provider", "notification-service", "high")
        ]
        
        for i, (title, service, severity) in enumerate(incident_types):
            started = datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))
            demo_incidents.append({
                "incident_id": str(uuid.uuid4()),
                "title": title,
                "service": service,
                "severity": severity,
                "status": random.choice(["investigating", "identified", "monitoring", "resolved"]),
                "started_at": started.isoformat(),
                "resolved_at": (started + timedelta(hours=random.randint(1, 5))).isoformat() if random.random() > 0.3 else None,
                "root_cause": random.choice([
                    "Increased traffic from marketing campaign",
                    "Memory leak in recent deployment",
                    "Third-party service degradation",
                    "Configuration drift after update",
                    None
                ]),
                "timeline": [
                    {"time": started.isoformat(), "action": "Incident detected by monitoring"},
                    {"time": (started + timedelta(minutes=5)).isoformat(), "action": "On-call engineer notified"},
                    {"time": (started + timedelta(minutes=15)).isoformat(), "action": "Root cause identified"}
                ]
            })
        return {"incidents": demo_incidents, "count": len(demo_incidents)}
    
    return {"incidents": incidents, "count": len(incidents)}

@app.post("/api/incidents")
async def create_incident(title: str, service: str, severity: str):
    """Create a new incident"""
    incident = {
        "incident_id": str(uuid.uuid4()),
        "title": title,
        "service": service,
        "severity": severity,
        "status": "investigating",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "timeline": [
            {"time": datetime.now(timezone.utc).isoformat(), "action": "Incident created"}
        ]
    }
    incidents_collection.insert_one(incident)
    return {"status": "created", "incident_id": incident["incident_id"]}

@app.patch("/api/incidents/{incident_id}")
async def update_incident(incident_id: str, update: IncidentUpdate):
    """Update incident status"""
    update_data = {"status": update.status, "updated_at": datetime.now(timezone.utc).isoformat()}
    
    if update.status == "resolved":
        update_data["resolved_at"] = datetime.now(timezone.utc).isoformat()
    
    if update.notes:
        update_data["root_cause"] = update.notes
    
    result = incidents_collection.update_one(
        {"incident_id": incident_id},
        {"$set": update_data}
    )
    
    return {"status": "updated"}

@app.get("/api/incidents/{incident_id}/analyze")
async def analyze_incident(incident_id: str):
    """Get AI analysis for an incident"""
    # Create sample incident for demo
    incident = {
        "title": "High latency in payment-service",
        "service": "payment-service",
        "severity": "critical",
        "duration": "45 minutes"
    }
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"incident-{incident_id}",
            system_message="You are an expert incident analyst. Provide root cause analysis and recommendations."
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(
            text=f"""Analyze this incident:
Title: {incident['title']}
Service: {incident['service']}
Severity: {incident['severity']}
Duration: {incident['duration']}

Provide:
1. Likely root causes (top 3)
2. Recommended immediate actions
3. Prevention measures for the future
4. Similar incidents to check for patterns"""
        ))
        
        return {
            "incident_id": incident_id,
            "analysis": response,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "incident_id": incident_id,
            "analysis": f"AI analysis unavailable: {str(e)}",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

# ----- System Status -----

@app.get("/api/system/status")
async def get_system_status():
    """Get overall system status"""
    return {
        "status": "operational",
        "services": {s: random.choice(["operational", "degraded", "operational", "operational"]) for s in SERVICES},
        "last_incident": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48))).isoformat(),
        "uptime_30d": round(random.uniform(99.5, 99.99), 2),
        "checked_at": datetime.now(timezone.utc).isoformat()
    }

# ----- Initialize Demo Data -----

@app.post("/api/demo/seed")
async def seed_demo_data():
    """Seed database with demo data"""
    # Clear existing data
    metrics_collection.delete_many({})
    logs_collection.delete_many({})
    
    # Generate and insert data
    metrics = generate_historical_metrics(hours=24)
    metrics_collection.insert_many(metrics)
    
    logs = generate_logs(500)
    logs_collection.insert_many(logs)
    
    return {
        "status": "seeded",
        "metrics_count": len(metrics),
        "logs_count": len(logs)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
