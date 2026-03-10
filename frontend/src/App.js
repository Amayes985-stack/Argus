import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { format, parseISO, formatDistanceToNow } from 'date-fns';
import {
  Activity, Server, AlertTriangle, Zap, Clock, Search,
  TrendingUp, Database, Wifi, Shield, Brain, RefreshCw,
  ChevronRight, Bell, Settings, Menu, X, CheckCircle,
  AlertCircle, Info, ArrowUp, ArrowDown, Loader2
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Utility function
const cn = (...classes) => classes.filter(Boolean).join(' ');

// Custom Tooltip for Charts
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-background-card border border-white/10 rounded-md p-3 shadow-xl">
        <p className="text-xs font-mono text-slate-400 mb-1">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm font-mono" style={{ color: entry.color }}>
            {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// Status Badge Component
const StatusBadge = ({ status }) => {
  const styles = {
    healthy: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    operational: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    degraded: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    critical: 'bg-red-500/20 text-red-400 border-red-500/30',
    active: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    acknowledged: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    resolved: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
    investigating: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    identified: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    monitoring: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  };

  return (
    <span className={cn(
      'px-2 py-0.5 text-xs font-mono rounded border inline-flex items-center gap-1',
      styles[status] || styles.healthy
    )}>
      <span className={cn(
        'w-1.5 h-1.5 rounded-full',
        status === 'healthy' || status === 'operational' || status === 'resolved' ? 'bg-emerald-400' :
        status === 'warning' || status === 'degraded' ? 'bg-amber-400' :
        status === 'critical' ? 'bg-red-400 animate-pulse' : 'bg-blue-400'
      )} />
      {status}
    </span>
  );
};

// Severity Badge
const SeverityBadge = ({ severity }) => {
  const styles = {
    low: 'bg-slate-500/20 text-slate-400',
    medium: 'bg-yellow-500/20 text-yellow-400',
    high: 'bg-orange-500/20 text-orange-400',
    critical: 'bg-red-500/20 text-red-400',
  };

  return (
    <span className={cn('px-2 py-0.5 text-xs font-mono rounded', styles[severity] || styles.low)}>
      {severity}
    </span>
  );
};

// Metric Card Component
const MetricCard = ({ title, value, unit, icon: Icon, trend, trendValue, loading }) => (
  <div className="card p-4 animate-slide-in" data-testid={`metric-card-${title.toLowerCase().replace(/\s+/g, '-')}`}>
    <div className="flex items-start justify-between mb-3">
      <span className="metric-label">{title}</span>
      <Icon className="w-4 h-4 text-slate-500" />
    </div>
    {loading ? (
      <div className="skeleton h-10 w-24 mb-2" />
    ) : (
      <div className="flex items-end gap-2">
        <span className="metric-value text-white">{value}</span>
        <span className="text-slate-500 text-sm mb-1">{unit}</span>
      </div>
    )}
    {trend && (
      <div className={cn(
        'flex items-center gap-1 mt-2 text-xs',
        trend === 'up' ? 'text-emerald-400' : 'text-red-400'
      )}>
        {trend === 'up' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
        {trendValue}
      </div>
    )}
  </div>
);

// Service Health Card
const ServiceHealthCard = ({ service, data }) => (
  <div className="card p-4 hover:border-primary/30 transition-colors" data-testid={`service-health-${service}`}>
    <div className="flex items-center justify-between mb-3">
      <span className="font-medium text-sm text-white">{service}</span>
      <StatusBadge status={data.status} />
    </div>
    <div className="grid grid-cols-2 gap-4 text-sm">
      <div>
        <span className="metric-label">Latency</span>
        <p className="font-mono text-white">{data.avg_latency}ms</p>
      </div>
      <div>
        <span className="metric-label">Error Rate</span>
        <p className={cn('font-mono', data.error_rate > 5 ? 'text-red-400' : 'text-white')}>
          {data.error_rate}%
        </p>
      </div>
    </div>
  </div>
);

// Server Card
const ServerCard = ({ server }) => (
  <div className="card p-4" data-testid={`server-card-${server.host}`}>
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center gap-2">
        <Server className="w-4 h-4 text-slate-400" />
        <span className="font-mono text-sm text-white">{server.host}</span>
      </div>
      <StatusBadge status={server.status} />
    </div>
    <div className="space-y-2">
      <div className="flex justify-between text-xs">
        <span className="text-slate-500">CPU</span>
        <span className={cn('font-mono', server.cpu > 85 ? 'text-red-400' : 'text-white')}>{server.cpu}%</span>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-1.5">
        <div 
          className={cn('h-1.5 rounded-full transition-all', 
            server.cpu > 85 ? 'bg-red-500' : server.cpu > 70 ? 'bg-amber-500' : 'bg-emerald-500'
          )} 
          style={{ width: `${server.cpu}%` }}
        />
      </div>
      <div className="flex justify-between text-xs mt-2">
        <span className="text-slate-500">Memory</span>
        <span className={cn('font-mono', server.memory > 90 ? 'text-red-400' : 'text-white')}>{server.memory}%</span>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-1.5">
        <div 
          className={cn('h-1.5 rounded-full transition-all',
            server.memory > 90 ? 'bg-red-500' : server.memory > 80 ? 'bg-amber-500' : 'bg-emerald-500'
          )} 
          style={{ width: `${server.memory}%` }}
        />
      </div>
      <div className="flex justify-between text-xs mt-2">
        <span className="text-slate-500">Disk</span>
        <span className="font-mono text-white">{server.disk}%</span>
      </div>
    </div>
  </div>
);

// Alert Item
const AlertItem = ({ alert, onExplain }) => (
  <div className="card p-4 border-l-2 border-l-primary" data-testid={`alert-${alert.alert_id}`}>
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <SeverityBadge severity={alert.severity} />
          <StatusBadge status={alert.status} />
        </div>
        <p className="text-sm text-white mb-1">{alert.message}</p>
        <p className="text-xs text-slate-500">
          {alert.service} • {alert.metric_type} • {formatDistanceToNow(parseISO(alert.created_at), { addSuffix: true })}
        </p>
      </div>
      <button 
        onClick={() => onExplain(alert)}
        className="text-xs text-primary hover:text-primary-hover flex items-center gap-1"
        data-testid={`explain-alert-${alert.alert_id}`}
      >
        <Brain className="w-3 h-3" /> AI Explain
      </button>
    </div>
  </div>
);

// Prediction Card
const PredictionCard = ({ prediction, onExplain }) => (
  <div className="card p-4 border-l-2 border-l-amber-500" data-testid={`prediction-${prediction.prediction_id}`}>
    <div className="flex items-center gap-2 mb-2">
      <TrendingUp className="w-4 h-4 text-amber-400" />
      <span className="text-sm font-medium text-white">{prediction.service}</span>
    </div>
    <p className="text-sm text-slate-300 mb-2">
      <span className="font-mono text-amber-400">{prediction.metric_type}</span> predicted to breach threshold
    </p>
    <div className="grid grid-cols-2 gap-3 text-xs mb-3">
      <div>
        <span className="text-slate-500">Current</span>
        <p className="font-mono text-white">{prediction.current_value}</p>
      </div>
      <div>
        <span className="text-slate-500">Predicted</span>
        <p className="font-mono text-red-400">{prediction.predicted_value}</p>
      </div>
      <div>
        <span className="text-slate-500">Time to Breach</span>
        <p className="font-mono text-amber-400">{prediction.hours_until_breach}h</p>
      </div>
      <div>
        <span className="text-slate-500">Confidence</span>
        <p className="font-mono text-white">{prediction.confidence}%</p>
      </div>
    </div>
    <button 
      onClick={() => onExplain(prediction)}
      className="w-full py-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 text-xs rounded flex items-center justify-center gap-1 transition-colors"
      data-testid={`explain-prediction-${prediction.prediction_id}`}
    >
      <Brain className="w-3 h-3" /> Get AI Prevention Plan
    </button>
  </div>
);

// Log Entry
const LogEntry = ({ log }) => {
  const levelColors = {
    info: 'text-blue-400',
    warn: 'text-yellow-400',
    error: 'text-red-400',
    critical: 'text-red-500 font-semibold',
  };

  return (
    <div className="flex items-start gap-3 py-2 border-b border-white/5 last:border-0 hover:bg-white/5 px-2 -mx-2 rounded" data-testid={`log-entry-${log.log_id}`}>
      <span className={cn('text-xs font-mono w-16 uppercase', levelColors[log.level])}>
        {log.level}
      </span>
      <span className="text-xs text-slate-500 font-mono w-32">
        {format(parseISO(log.timestamp), 'HH:mm:ss')}
      </span>
      <span className="text-xs text-slate-400 font-mono w-28">{log.service}</span>
      <span className="text-xs text-slate-300 flex-1">{log.message}</span>
    </div>
  );
};

// Incident Timeline Item
const IncidentItem = ({ incident, onAnalyze }) => (
  <div className="card p-4" data-testid={`incident-${incident.incident_id}`}>
    <div className="flex items-start justify-between mb-2">
      <div>
        <h4 className="text-sm font-medium text-white">{incident.title}</h4>
        <p className="text-xs text-slate-500">{incident.service}</p>
      </div>
      <div className="flex items-center gap-2">
        <SeverityBadge severity={incident.severity} />
        <StatusBadge status={incident.status} />
      </div>
    </div>
    <div className="flex items-center gap-4 text-xs text-slate-400 mb-3">
      <span className="flex items-center gap-1">
        <Clock className="w-3 h-3" />
        {formatDistanceToNow(parseISO(incident.started_at), { addSuffix: true })}
      </span>
      {incident.resolved_at && (
        <span className="flex items-center gap-1 text-emerald-400">
          <CheckCircle className="w-3 h-3" /> Resolved
        </span>
      )}
    </div>
    {incident.root_cause && (
      <p className="text-xs text-slate-300 bg-slate-800/50 p-2 rounded mb-2">
        Root cause: {incident.root_cause}
      </p>
    )}
    <button 
      onClick={() => onAnalyze(incident)}
      className="text-xs text-primary hover:text-primary-hover flex items-center gap-1"
      data-testid={`analyze-incident-${incident.incident_id}`}
    >
      <Brain className="w-3 h-3" /> AI Analysis
    </button>
  </div>
);

// AI Explanation Modal
const AIExplanationModal = ({ isOpen, onClose, title, content, loading }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4" data-testid="ai-explanation-modal">
      <div className="bg-background-card border border-white/10 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden animate-slide-in">
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary" />
            <h3 className="font-heading font-semibold text-white">{title}</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white" data-testid="close-modal-btn">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-4 overflow-y-auto max-h-[60vh]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
              <span className="ml-3 text-slate-400">Analyzing with AI...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {typeof content === 'string' ? (
                <p className="text-slate-300 whitespace-pre-wrap">{content}</p>
              ) : (
                Object.entries(content || {}).map(([key, value]) => (
                  <div key={key} className="bg-slate-800/50 rounded-lg p-4">
                    <h4 className="text-xs font-mono text-primary uppercase tracking-wider mb-2">
                      {key.replace(/_/g, ' ')}
                    </h4>
                    {Array.isArray(value) ? (
                      <ul className="space-y-1">
                        {value.map((item, i) => (
                          <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                            <ChevronRight className="w-4 h-4 text-slate-500 mt-0.5 flex-shrink-0" />
                            {item}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-slate-300">{value}</p>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Navigation
const Navigation = ({ activeTab, setActiveTab, overview }) => {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'infrastructure', label: 'Infrastructure', icon: Server },
    { id: 'applications', label: 'Applications', icon: Database },
    { id: 'alerts', label: 'Alerts', icon: Bell, badge: overview?.active_alerts },
    { id: 'predictions', label: 'Predictions', icon: TrendingUp, badge: overview?.active_predictions },
    { id: 'incidents', label: 'Incidents', icon: AlertTriangle },
    { id: 'logs', label: 'Logs', icon: Search },
  ];

  return (
    <nav className="bg-background-surface border-b border-white/10 sticky top-0 z-40 backdrop-blur-xl">
      <div className="max-w-[1600px] mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <span className="font-heading font-bold text-lg text-white">Sentinels</span>
            </div>
            <div className="hidden md:flex items-center gap-1">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    'px-4 py-2 text-sm font-medium rounded-md transition-colors flex items-center gap-2',
                    activeTab === tab.id 
                      ? 'bg-primary/10 text-primary' 
                      : 'text-slate-400 hover:text-white hover:bg-white/5'
                  )}
                  data-testid={`nav-${tab.id}`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                  {tab.badge > 0 && (
                    <span className="ml-1 px-1.5 py-0.5 text-xs bg-red-500 text-white rounded-full">
                      {tab.badge}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-md" data-testid="settings-btn">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

// Main App Component
function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [servers, setServers] = useState([]);
  const [services, setServices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [logs, setLogs] = useState([]);
  const [metricsTimeseries, setMetricsTimeseries] = useState([]);
  
  // AI Modal State
  const [aiModal, setAiModal] = useState({ isOpen: false, title: '', content: null, loading: false });
  
  // Log filters
  const [logFilter, setLogFilter] = useState({ service: '', level: '', search: '' });

  const fetchOverview = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/dashboard/overview`);
      setOverview(res.data);
    } catch (err) {
      console.error('Failed to fetch overview:', err);
    }
  }, []);

  const fetchServers = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/infrastructure/servers`);
      setServers(res.data.servers);
    } catch (err) {
      console.error('Failed to fetch servers:', err);
    }
  }, []);

  const fetchServices = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/applications/services`);
      setServices(res.data.services);
    } catch (err) {
      console.error('Failed to fetch services:', err);
    }
  }, []);

  const fetchAlerts = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/alerts`);
      setAlerts(res.data.alerts);
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
    }
  }, []);

  const fetchPredictions = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/predictions`);
      setPredictions(res.data.predictions);
    } catch (err) {
      console.error('Failed to fetch predictions:', err);
    }
  }, []);

  const fetchAnomalies = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/anomalies`);
      setAnomalies(res.data.anomalies);
    } catch (err) {
      console.error('Failed to fetch anomalies:', err);
    }
  }, []);

  const fetchIncidents = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/incidents`);
      setIncidents(res.data.incidents);
    } catch (err) {
      console.error('Failed to fetch incidents:', err);
    }
  }, []);

  const fetchLogs = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (logFilter.service) params.append('service', logFilter.service);
      if (logFilter.level) params.append('level', logFilter.level);
      if (logFilter.search) params.append('search', logFilter.search);
      
      const res = await axios.get(`${API_URL}/api/logs?${params}`);
      setLogs(res.data.logs);
    } catch (err) {
      console.error('Failed to fetch logs:', err);
    }
  }, [logFilter]);

  const fetchMetricsTimeseries = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/metrics/timeseries?service=api-gateway&metric_type=latency&hours=6`);
      setMetricsTimeseries(res.data.data.map(d => ({
        ...d,
        time: format(parseISO(d.timestamp), 'HH:mm')
      })));
    } catch (err) {
      console.error('Failed to fetch timeseries:', err);
    }
  }, []);

  // Initial data load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchOverview(),
        fetchServers(),
        fetchServices(),
        fetchAlerts(),
        fetchPredictions(),
        fetchAnomalies(),
        fetchIncidents(),
        fetchLogs(),
        fetchMetricsTimeseries()
      ]);
      setLoading(false);
    };
    loadData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchOverview();
      fetchServers();
      fetchServices();
      fetchAlerts();
    }, 30000);

    return () => clearInterval(interval);
  }, [fetchOverview, fetchServers, fetchServices, fetchAlerts, fetchPredictions, fetchAnomalies, fetchIncidents, fetchLogs, fetchMetricsTimeseries]);

  // Refetch logs when filter changes
  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  // AI Explanation handlers
  const handleExplainAlert = async (alert) => {
    setAiModal({ isOpen: true, title: 'AI Alert Analysis', content: null, loading: true });
    try {
      const res = await axios.post(`${API_URL}/api/anomalies/explain`, {
        service: alert.service,
        metric_type: alert.metric_type,
        value: alert.value,
        severity: alert.severity,
        detection_method: 'threshold'
      });
      setAiModal(prev => ({ ...prev, content: res.data.explanation, loading: false }));
    } catch (err) {
      setAiModal(prev => ({ ...prev, content: 'Failed to generate AI explanation', loading: false }));
    }
  };

  const handleExplainPrediction = async (prediction) => {
    setAiModal({ isOpen: true, title: 'AI Prevention Plan', content: null, loading: true });
    try {
      const res = await axios.post(`${API_URL}/api/predictions/explain`, prediction);
      setAiModal(prev => ({ ...prev, content: res.data.explanation, loading: false }));
    } catch (err) {
      setAiModal(prev => ({ ...prev, content: 'Failed to generate AI explanation', loading: false }));
    }
  };

  const handleAnalyzeIncident = async (incident) => {
    setAiModal({ isOpen: true, title: 'AI Incident Analysis', content: null, loading: true });
    try {
      const res = await axios.get(`${API_URL}/api/incidents/${incident.incident_id}/analyze`);
      setAiModal(prev => ({ ...prev, content: res.data.analysis, loading: false }));
    } catch (err) {
      setAiModal(prev => ({ ...prev, content: 'Failed to generate AI analysis', loading: false }));
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    await Promise.all([
      fetchOverview(),
      fetchServers(),
      fetchServices(),
      fetchAlerts(),
      fetchPredictions(),
      fetchAnomalies()
    ]);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-background" data-testid="app-container">
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} overview={overview} />
      
      <main className="max-w-[1600px] mx-auto p-6">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6 animate-fade-in" data-testid="dashboard-view">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="font-heading text-2xl font-bold text-white">System Overview</h1>
                <p className="text-sm text-slate-400">
                  Last updated: {overview?.last_updated ? format(parseISO(overview.last_updated), 'HH:mm:ss') : '--'}
                </p>
              </div>
              <button 
                onClick={handleRefresh}
                className="flex items-center gap-2 px-4 py-2 bg-primary/10 hover:bg-primary/20 text-primary rounded-md transition-colors"
                data-testid="refresh-btn"
              >
                <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
                Refresh
              </button>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard 
                title="Total Services" 
                value={overview?.total_services || 0} 
                unit="" 
                icon={Database}
                loading={loading}
              />
              <MetricCard 
                title="Healthy Services" 
                value={overview?.healthy_services || 0} 
                unit={`/ ${overview?.total_services || 0}`}
                icon={CheckCircle}
                trend="up"
                trendValue="100% uptime"
                loading={loading}
              />
              <MetricCard 
                title="Active Anomalies" 
                value={overview?.active_anomalies || 0} 
                unit="" 
                icon={AlertCircle}
                loading={loading}
              />
              <MetricCard 
                title="Predictions" 
                value={overview?.active_predictions || 0} 
                unit="active" 
                icon={TrendingUp}
                loading={loading}
              />
            </div>

            {/* Service Health Grid */}
            <div>
              <h2 className="font-heading text-lg font-semibold text-white mb-4">Service Health</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                {overview?.services_health && Object.entries(overview.services_health).map(([service, data]) => (
                  <ServiceHealthCard key={service} service={service} data={data} />
                ))}
              </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Latency Chart */}
              <div className="card p-4">
                <h3 className="text-sm font-medium text-white mb-4">API Gateway Latency (6h)</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart data={metricsTimeseries}>
                    <defs>
                      <linearGradient id="latencyGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
                    <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="value" stroke="#3b82f6" fill="url(#latencyGradient)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Anomaly Distribution */}
              <div className="card p-4">
                <h3 className="text-sm font-medium text-white mb-4">Anomalies by Severity</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={[
                    { severity: 'Critical', count: anomalies.filter(a => a.severity === 'critical').length, fill: '#ef4444' },
                    { severity: 'High', count: anomalies.filter(a => a.severity === 'high').length, fill: '#f97316' },
                    { severity: 'Medium', count: anomalies.filter(a => a.severity === 'medium').length, fill: '#eab308' },
                    { severity: 'Low', count: anomalies.filter(a => a.severity === 'low').length, fill: '#64748b' },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
                    <XAxis dataKey="severity" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Recent Alerts & Predictions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-heading text-lg font-semibold text-white">Recent Alerts</h2>
                  <button 
                    onClick={() => setActiveTab('alerts')}
                    className="text-sm text-primary hover:text-primary-hover flex items-center gap-1"
                    data-testid="view-all-alerts"
                  >
                    View all <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
                <div className="space-y-3">
                  {alerts.slice(0, 3).map(alert => (
                    <AlertItem key={alert.alert_id} alert={alert} onExplain={handleExplainAlert} />
                  ))}
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-heading text-lg font-semibold text-white">Active Predictions</h2>
                  <button 
                    onClick={() => setActiveTab('predictions')}
                    className="text-sm text-primary hover:text-primary-hover flex items-center gap-1"
                    data-testid="view-all-predictions"
                  >
                    View all <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
                <div className="space-y-3">
                  {predictions.slice(0, 2).map(pred => (
                    <PredictionCard key={pred.prediction_id} prediction={pred} onExplain={handleExplainPrediction} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Infrastructure Tab */}
        {activeTab === 'infrastructure' && (
          <div className="space-y-6 animate-fade-in" data-testid="infrastructure-view">
            <div className="flex items-center justify-between">
              <h1 className="font-heading text-2xl font-bold text-white">Infrastructure Monitoring</h1>
              <button onClick={fetchServers} className="flex items-center gap-2 px-4 py-2 bg-primary/10 hover:bg-primary/20 text-primary rounded-md" data-testid="refresh-servers">
                <RefreshCw className="w-4 h-4" /> Refresh
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {servers.map(server => (
                <ServerCard key={server.host} server={server} />
              ))}
            </div>
          </div>
        )}

        {/* Applications Tab */}
        {activeTab === 'applications' && (
          <div className="space-y-6 animate-fade-in" data-testid="applications-view">
            <div className="flex items-center justify-between">
              <h1 className="font-heading text-2xl font-bold text-white">Application Monitoring</h1>
              <button onClick={fetchServices} className="flex items-center gap-2 px-4 py-2 bg-primary/10 hover:bg-primary/20 text-primary rounded-md" data-testid="refresh-services">
                <RefreshCw className="w-4 h-4" /> Refresh
              </button>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
              {services.map(service => (
                <div key={service.service} className="card p-4" data-testid={`app-service-${service.service}`}>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4 text-slate-400" />
                      <span className="font-mono text-sm text-white">{service.service}</span>
                    </div>
                    <StatusBadge status={service.status} />
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <span className="metric-label">P50</span>
                      <p className="font-mono text-lg text-white">{service.latency_p50}ms</p>
                    </div>
                    <div>
                      <span className="metric-label">P95</span>
                      <p className="font-mono text-lg text-amber-400">{service.latency_p95}ms</p>
                    </div>
                    <div>
                      <span className="metric-label">P99</span>
                      <p className={cn('font-mono text-lg', service.latency_p99 > 500 ? 'text-red-400' : 'text-white')}>
                        {service.latency_p99}ms
                      </p>
                    </div>
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-white/5 grid grid-cols-2 gap-4">
                    <div>
                      <span className="metric-label">Success Rate</span>
                      <p className={cn('font-mono text-lg', service.success_rate < 99 ? 'text-amber-400' : 'text-emerald-400')}>
                        {service.success_rate}%
                      </p>
                    </div>
                    <div>
                      <span className="metric-label">Req/min</span>
                      <p className="font-mono text-lg text-white">{service.request_count}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <div className="space-y-6 animate-fade-in" data-testid="alerts-view">
            <div className="flex items-center justify-between">
              <h1 className="font-heading text-2xl font-bold text-white">Alerts</h1>
              <div className="flex items-center gap-2">
                <span className="text-sm text-slate-400">{alerts.length} total</span>
              </div>
            </div>
            
            <div className="space-y-3">
              {alerts.map(alert => (
                <AlertItem key={alert.alert_id} alert={alert} onExplain={handleExplainAlert} />
              ))}
            </div>
          </div>
        )}

        {/* Predictions Tab */}
        {activeTab === 'predictions' && (
          <div className="space-y-6 animate-fade-in" data-testid="predictions-view">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="font-heading text-2xl font-bold text-white">Failure Predictions</h1>
                <p className="text-sm text-slate-400">AI-powered predictions of potential system issues</p>
              </div>
              <button onClick={fetchPredictions} className="flex items-center gap-2 px-4 py-2 bg-primary/10 hover:bg-primary/20 text-primary rounded-md" data-testid="refresh-predictions">
                <RefreshCw className="w-4 h-4" /> Refresh
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {predictions.map(pred => (
                <PredictionCard key={pred.prediction_id} prediction={pred} onExplain={handleExplainPrediction} />
              ))}
              {predictions.length === 0 && (
                <div className="col-span-full text-center py-12">
                  <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
                  <p className="text-slate-400">No critical predictions at this time</p>
                  <p className="text-sm text-slate-500">System is running within expected parameters</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Incidents Tab */}
        {activeTab === 'incidents' && (
          <div className="space-y-6 animate-fade-in" data-testid="incidents-view">
            <div className="flex items-center justify-between">
              <h1 className="font-heading text-2xl font-bold text-white">Incident Timeline</h1>
            </div>
            
            <div className="space-y-4">
              {incidents.map(incident => (
                <IncidentItem key={incident.incident_id} incident={incident} onAnalyze={handleAnalyzeIncident} />
              ))}
            </div>
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div className="space-y-6 animate-fade-in" data-testid="logs-view">
            <div className="flex items-center justify-between">
              <h1 className="font-heading text-2xl font-bold text-white">Log Explorer</h1>
            </div>
            
            {/* Filters */}
            <div className="card p-4">
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <label className="metric-label mb-1 block">Search</label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input
                      type="text"
                      value={logFilter.search}
                      onChange={(e) => setLogFilter(prev => ({ ...prev, search: e.target.value }))}
                      placeholder="Search logs..."
                      className="w-full pl-10 pr-4 py-2 bg-black/20 border border-white/10 rounded-md text-sm text-white placeholder:text-slate-600 focus:border-primary/50 focus:outline-none"
                      data-testid="log-search-input"
                    />
                  </div>
                </div>
                <div>
                  <label className="metric-label mb-1 block">Service</label>
                  <select
                    value={logFilter.service}
                    onChange={(e) => setLogFilter(prev => ({ ...prev, service: e.target.value }))}
                    className="px-4 py-2 bg-black/20 border border-white/10 rounded-md text-sm text-white focus:border-primary/50 focus:outline-none"
                    data-testid="log-service-filter"
                  >
                    <option value="">All services</option>
                    {['api-gateway', 'user-service', 'payment-service', 'inventory-service', 'notification-service'].map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="metric-label mb-1 block">Level</label>
                  <select
                    value={logFilter.level}
                    onChange={(e) => setLogFilter(prev => ({ ...prev, level: e.target.value }))}
                    className="px-4 py-2 bg-black/20 border border-white/10 rounded-md text-sm text-white focus:border-primary/50 focus:outline-none"
                    data-testid="log-level-filter"
                  >
                    <option value="">All levels</option>
                    {['info', 'warn', 'error', 'critical'].map(l => (
                      <option key={l} value={l}>{l.toUpperCase()}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Log List */}
            <div className="card p-4 font-mono text-sm">
              <div className="flex items-center gap-3 py-2 border-b border-white/10 text-xs text-slate-500 uppercase tracking-wider">
                <span className="w-16">Level</span>
                <span className="w-32">Time</span>
                <span className="w-28">Service</span>
                <span className="flex-1">Message</span>
              </div>
              <div className="max-h-[600px] overflow-y-auto">
                {logs.map(log => (
                  <LogEntry key={log.log_id} log={log} />
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* AI Explanation Modal */}
      <AIExplanationModal 
        isOpen={aiModal.isOpen}
        onClose={() => setAiModal({ isOpen: false, title: '', content: null, loading: false })}
        title={aiModal.title}
        content={aiModal.content}
        loading={aiModal.loading}
      />
    </div>
  );
}

export default App;
