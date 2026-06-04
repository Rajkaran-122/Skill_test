import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, Clock, ShieldAlert } from 'lucide-react';
import { fetchWithAuth } from '../utils/api';

interface Anomaly {
  id: string;
  type: string;
  severity: string;
  store: string;
  zone: string;
  time: string;
  status: string;
  desc: string;
}

const Alerts: React.FC = () => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [resolvingId, setResolvingId] = useState<string | null>(null);

  const fetchAnomalies = async () => {
    try {
      const res = await fetchWithAuth('/api/v1/stores/STORE001/anomalies');
      if (res.ok) {
        const data = await res.json();
        setAnomalies(data.anomalies);
      }
    } catch (e) {
      console.error('Failed to fetch anomalies', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnomalies();
    // Poll every 5 seconds for new alerts
    const interval = setInterval(fetchAnomalies, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleResolve = async (id: string) => {
    setResolvingId(id);
    try {
      const res = await fetchWithAuth(`/api/v1/anomalies/${id}/resolve`, {
        method: 'POST',
      });
      if (res.ok) {
        // Optimistically remove from UI
        setAnomalies(prev => prev.filter(a => a.id !== id));
      }
    } catch (e) {
      console.error('Failed to resolve anomaly', e);
    } finally {
      setResolvingId(null);
    }
  };

  const getSeverityStyles = (severity: string) => {
    switch(severity) {
      case 'CRITICAL': return 'bg-red-500/20 text-red-400 border-red-500/50';
      case 'HIGH': return 'bg-orange-500/20 text-orange-400 border-orange-500/50';
      case 'MEDIUM': return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/50';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-3">
            <ShieldAlert className="w-7 h-7 text-red-500" />
            <span>AI Incident Inbox</span>
          </h1>
          <p className="text-gray-400 mt-1">Operational alerts requiring manager action</p>
        </div>
        <div className="bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg flex items-center space-x-2">
          <Clock className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-300">Active Queue: <span className="text-white font-bold">{anomalies.length}</span></span>
        </div>
      </div>

      <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-gray-700 bg-gray-900/50 flex items-center justify-between">
          <h3 className="font-semibold text-gray-300">Pending Actions</h3>
        </div>
        
        <div className="divide-y divide-gray-700/50">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading incidents...</div>
          ) : anomalies.length === 0 ? (
            <div className="p-12 text-center flex flex-col items-center justify-center">
              <CheckCircle className="w-12 h-12 text-green-500 mb-4 opacity-80" />
              <h3 className="text-xl font-bold text-white mb-2">Zero Active Incidents</h3>
              <p className="text-gray-400">All store operations are running smoothly.</p>
            </div>
          ) : (
            anomalies.map((alert) => (
              <div key={alert.id} className="p-5 hover:bg-gray-700/20 transition-colors flex items-center justify-between group">
                <div className="flex items-start space-x-4">
                  <div className={`mt-1 p-2 rounded-lg border ${getSeverityStyles(alert.severity)}`}>
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-3 mb-1">
                      <span className="text-white font-bold text-lg">{alert.type.replace('_', ' ')}</span>
                      <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${getSeverityStyles(alert.severity)}`}>
                        {alert.severity}
                      </span>
                      <span className="text-xs text-gray-500 font-mono">{alert.id}</span>
                    </div>
                    <p className="text-gray-300 mb-2">{alert.desc}</p>
                    <div className="flex items-center space-x-4 text-xs font-medium text-gray-500">
                      <span className="flex items-center"><Clock className="w-3 h-3 mr-1" /> Detected {alert.time}</span>
                      <span>•</span>
                      <span>Location: {alert.store}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <button
                    onClick={() => handleResolve(alert.id)}
                    disabled={resolvingId === alert.id}
                    className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg font-medium transition-all transform active:scale-95 disabled:opacity-50 shadow-lg shadow-indigo-600/20"
                  >
                    {resolvingId === alert.id ? (
                      <span className="animate-pulse">Resolving...</span>
                    ) : (
                      <>
                        <CheckCircle className="w-4 h-4" />
                        <span>Acknowledge & Resolve</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Alerts;
