import React, { useEffect, useState } from 'react';
import { Store as StoreIcon, AlertTriangle, TrendingUp, Users, MapPin, ChevronRight } from 'lucide-react';
import { fetchWithAuth } from '../utils/api';
import { useNavigate } from 'react-router-dom';

interface StoreHealth {
  id: string;
  name: string;
  city: string;
  status: 'OPTIMAL' | 'WARNING' | 'CRITICAL' | 'OFFLINE';
  visitors: number;
  conversion: number;
  alerts: number;
}

const mockStores = [
  { id: 'STORE001', name: 'Flagship Center', city: 'Mumbai', defaultStatus: 'OPTIMAL' },
  { id: 'STORE002', name: 'North Mall', city: 'Delhi', defaultStatus: 'OFFLINE' },
  { id: 'STORE003', name: 'Tech Park Outlet', city: 'Bangalore', defaultStatus: 'WARNING' },
];

const Stores: React.FC = () => {
  const [storeData, setStoreData] = useState<StoreHealth[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchFleetHealth = async () => {
      const results: StoreHealth[] = [];
      
      for (const store of mockStores) {
        try {
          // Attempt to fetch real metrics for each store
          const res = await fetchWithAuth(`/api/v1/stores/${store.id}/metrics`);
          if (res.ok) {
            const data = await res.json();
            const kpis = data.kpis;
            results.push({
              id: store.id,
              name: store.name,
              city: store.city,
              status: kpis.active_alerts > 0 ? 'WARNING' : 'OPTIMAL',
              visitors: kpis.visitors_today,
              conversion: kpis.conversion_rate,
              alerts: kpis.active_alerts
            });
          } else {
            // If API 404s (e.g. no data for STORE002 in DB), show as offline/mock
            results.push({
              id: store.id,
              name: store.name,
              city: store.city,
              status: 'OFFLINE',
              visitors: 0,
              conversion: 0,
              alerts: 0
            });
          }
        } catch (e) {
          results.push({
            id: store.id,
            name: store.name,
            city: store.city,
            status: 'OFFLINE',
            visitors: 0,
            conversion: 0,
            alerts: 0
          });
        }
      }
      
      setStoreData(results);
      setLoading(false);
    };

    fetchFleetHealth();
  }, []);

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'OPTIMAL': return 'bg-green-500/20 text-green-400 border-green-500/50';
      case 'WARNING': return 'bg-amber-500/20 text-amber-400 border-amber-500/50';
      case 'CRITICAL': return 'bg-red-500/20 text-red-400 border-red-500/50';
      default: return 'bg-gray-700/50 text-gray-400 border-gray-600';
    }
  };

  const getStatusDot = (status: string) => {
    switch(status) {
      case 'OPTIMAL': return 'bg-green-500';
      case 'WARNING': return 'bg-amber-500 animate-pulse';
      case 'CRITICAL': return 'bg-red-500 animate-pulse';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-3">
            <StoreIcon className="w-7 h-7 text-indigo-500" />
            <span>Fleet Management</span>
          </h1>
          <p className="text-gray-400 mt-1">Multi-tenant site health and operational status</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20 text-indigo-400">Loading fleet data...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {storeData.map((store) => (
            <div 
              key={store.id} 
              className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden shadow-xl hover:border-indigo-500/50 transition-all group"
            >
              <div className="p-5 border-b border-gray-700 bg-gray-900/40">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-4 h-4 text-indigo-400" />
                    <span className="text-sm font-medium text-indigo-300">{store.city}</span>
                  </div>
                  <div className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full border text-[10px] font-bold tracking-wider ${getStatusColor(store.status)}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${getStatusDot(store.status)}`}></span>
                    <span>{store.status}</span>
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white group-hover:text-indigo-400 transition-colors">
                  {store.name}
                </h3>
                <p className="text-xs text-gray-500 font-mono mt-1">{store.id}</p>
              </div>
              
              <div className="p-5 grid grid-cols-3 gap-4">
                <div className="flex flex-col items-center p-3 bg-gray-900/50 rounded-lg">
                  <Users className="w-5 h-5 text-blue-400 mb-1" />
                  <span className="text-lg font-bold text-white">{store.visitors}</span>
                  <span className="text-[10px] text-gray-400 uppercase tracking-wide">Footfall</span>
                </div>
                <div className="flex flex-col items-center p-3 bg-gray-900/50 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-green-400 mb-1" />
                  <span className="text-lg font-bold text-white">{store.conversion.toFixed(1)}%</span>
                  <span className="text-[10px] text-gray-400 uppercase tracking-wide">Conv.</span>
                </div>
                <div className="flex flex-col items-center p-3 bg-gray-900/50 rounded-lg relative overflow-hidden">
                  {store.alerts > 0 && <div className="absolute inset-0 bg-red-500/10 animate-pulse"></div>}
                  <AlertTriangle className={`w-5 h-5 mb-1 ${store.alerts > 0 ? 'text-red-400' : 'text-gray-500'}`} />
                  <span className="text-lg font-bold text-white relative z-10">{store.alerts}</span>
                  <span className="text-[10px] text-gray-400 uppercase tracking-wide relative z-10">Alerts</span>
                </div>
              </div>
              
              <div className="p-4 bg-gray-900 border-t border-gray-700">
                <button 
                  onClick={() => navigate(`/store/${store.id}`)}
                  disabled={store.status === 'OFFLINE'}
                  className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600 hover:text-white"
                >
                  <span>Enter Dashboard</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Stores;
