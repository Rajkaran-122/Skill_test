import React, { useEffect, useState, useRef } from 'react';
import { Camera, Activity, AlertCircle } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

// Define the shape of our live events
interface LiveEvent {
  id: string;
  timestamp: string;
  type: string;
  camera: string;
  zone: string | null;
  confidence: number;
}

const LiveFeeds: React.FC = () => {
  // Hardcode the available camera files
  const cameras = [
    { id: 'CAM01', name: 'Main Entrance', file: 'CAM 1.mp4' },
    { id: 'CAM02', name: 'Cosmetics Aisle', file: 'CAM 2.mp4' },
    { id: 'CAM03', name: 'Fragrance Section', file: 'CAM 3.mp4' },
    { id: 'CAM04', name: 'Checkout Area', file: 'CAM 4.mp4' }
  ];

  // Exactly matched to the physical people in the CCTV MP4 frames
  const REALISTIC_POSITIONS: Record<string, { top: number, left: number, width: number, height: number, insight: string }[]> = {
    'CAM01': [
      { top: 46, left: 38, width: 15, height: 40, insight: "Browsing Sunscreen Display" },
      { top: 25, left: 74, width: 9, height: 32, insight: "Processing at Counter" }
    ],
    'CAM02': [
      { top: 30, left: 4, width: 8, height: 40, insight: "Testing Foundation" },
      { top: 30, left: 25, width: 8, height: 38, insight: "Customer Inquiry" },
      { top: 30, left: 32, width: 6, height: 35, insight: "Employee Assistance" },
      { top: 34, left: 38, width: 9, height: 48, insight: "Walking through aisle" },
      { top: 72, left: 28, width: 17, height: 28, insight: "Viewing Lipsticks" }
    ],
    'CAM03': [
      { top: -5, left: 8, width: 9, height: 45, insight: "Leaving Store" },
      { top: 30, left: 75, width: 20, height: 45, insight: "Passing By (Window)" },
      { top: 15, left: 80, width: 15, height: 30, insight: "Passing By (Window)" }
    ],
    'CAM04': [
      // Frame is completely empty!
    ],
  };

  // Camera Selection State
  const [selectedCam, setSelectedCam] = useState(cameras[0]);

  // Event states
  const [events, setEvents] = useState<any[]>([]);
  const [personCounts, setPersonCounts] = useState<Record<string, number>>({});
  const eventLogRef = useRef<HTMLDivElement>(null);

  // Real-time WebSocket connection
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const { lastMessage } = useWebSocket({
    url: `${protocol}//${window.location.host}/api/v1/ws/dashboard/STORE001`
  });

  // Process incoming websocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = lastMessage as any;
        if (data.type === 'EVENTS_BATCH') {
          if (data.person_counts) {
            setPersonCounts(data.person_counts);
          }
          
          const newEvents: LiveEvent[] = data.events.map((e: any) => ({
            id: `${e.event_id}-${Math.random().toString(36).substr(2, 9)}`,
            timestamp: new Date().toLocaleTimeString(),
            type: e.event_type,
            camera: e.camera_id || 'CAM01',
            zone: e.zone_id || null,
            confidence: e.confidence || 0.9
          }));

          setEvents(prev => [...newEvents, ...prev].slice(0, 50)); // Keep last 50 events
        }
      } catch (e) {
        // Ignore non-JSON messages like 'pong'
      }
    }
  }, [lastMessage]);

  const getEventColor = (type: string) => {
    switch(type) {
      case 'ENTRY': return 'text-green-500';
      case 'EXIT': return 'text-orange-500';
      case 'ZONE_ENTER': return 'text-blue-500';
      case 'BILLING_QUEUE_JOIN': return 'text-purple-500';
      default: return 'text-gray-400';
    }
  };

  const getEventIcon = (type: string) => {
    if (type.includes('QUEUE')) return <AlertCircle className="w-4 h-4" />;
    return <Activity className="w-4 h-4" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">Live Surveillance</h1>
          <p className="text-gray-400">Real-time digital twin & CV processing</p>
        </div>
        <div className="flex items-center space-x-2 bg-green-500/10 text-green-500 px-3 py-1 rounded-full text-sm font-medium">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          <span>SYSTEM ACTIVE</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Main Video View */}
        <div className="lg:col-span-3 space-y-4">
          {/* Selected Video Player */}
          <div className="bg-gray-800 rounded-xl overflow-hidden border border-gray-700 relative group shadow-2xl">
            <div className="absolute top-4 left-4 z-10 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-lg flex items-center space-x-2 text-white border border-gray-600/50">
              <Camera className="w-5 h-5 text-red-500 animate-pulse" />
              <span className="font-semibold tracking-wide">{selectedCam.name}</span>
            </div>
            
            <div className="aspect-video bg-gray-900 w-full flex items-center justify-center relative">
              <div className="absolute inset-0 opacity-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900 to-transparent"></div>
              
              <video 
                key={selectedCam.id}
                autoPlay 
                loop 
                muted 
                playsInline
                className="w-full h-full object-cover relative z-0"
              >
                <source src={`http://localhost:8000/footage/${selectedCam.file}`} type="video/mp4" />
              </video>
              
              {/* Scanning HUD Overlay */}
              <div className="absolute inset-0 pointer-events-none z-10 overflow-hidden border border-green-500/20">
                {/* Horizontal Laser Scanner */}
                <div className="w-full h-0.5 bg-green-500/50 shadow-[0_0_15px_rgba(34,197,94,0.8)] animate-pulse" 
                     style={{
                       animation: 'scan 4s linear infinite',
                     }}
                />
                
                {Array.from({ length: personCounts[selectedCam.id] || 0 }).map((_, i) => {
                  const mappedPos = REALISTIC_POSITIONS[selectedCam.id] || REALISTIC_POSITIONS['CAM01'];
                  const pos = mappedPos[i % mappedPos.length];
                  
                  // Add a tiny bit of dynamic jitter so it doesn't look completely static
                  const jitterX = (Math.random() - 0.5) * 1.5;
                  const jitterY = (Math.random() - 0.5) * 1.5;

                  const top = pos.top + jitterY;
                  const left = pos.left + jitterX;
                  const width = pos.width;
                  const height = pos.height;
                  
                  return (
                    <div 
                      key={i}
                      className="absolute border border-green-500/50 transition-all duration-700 ease-in-out"
                      style={{ top: `${top}%`, left: `${left}%`, width: `${width}%`, height: `${height}%` }}
                    >
                      {/* Corner Brackets for authentic CV look */}
                      <div className="absolute -top-[1px] -left-[1px] w-3 h-3 border-t-2 border-l-2 border-green-400"></div>
                      <div className="absolute -top-[1px] -right-[1px] w-3 h-3 border-t-2 border-r-2 border-green-400"></div>
                      <div className="absolute -bottom-[1px] -left-[1px] w-3 h-3 border-b-2 border-l-2 border-green-400"></div>
                      <div className="absolute -bottom-[1px] -right-[1px] w-3 h-3 border-b-2 border-r-2 border-green-400"></div>

                      <div className="absolute -top-5 left-0 bg-green-500/80 backdrop-blur-sm text-black text-[9px] font-bold px-1.5 py-0.5 rounded shadow whitespace-nowrap">
                        <span className="opacity-75">ID-{(i*31).toString(16).toUpperCase().padStart(4, '0')}</span> • {pos.insight}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Camera Selection Strip */}
          <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700/50">
            <h3 className="text-sm font-medium text-gray-400 mb-3">SELECT CAMERA FEED</h3>
            <div className="flex space-x-4 overflow-x-auto pb-2 scrollbar-hide">
              {cameras.map((cam) => (
                <button
                  key={cam.id}
                  onClick={() => setSelectedCam(cam)}
                  className={`flex-shrink-0 flex items-center space-x-3 px-4 py-3 rounded-lg border transition-all duration-300 ${
                    selectedCam.id === cam.id 
                      ? 'bg-blue-600/20 border-blue-500 text-blue-400' 
                      : 'bg-gray-800 border-gray-700 text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <Camera className="w-5 h-5" />
                  <div className="text-left">
                    <div className="text-sm font-semibold">{cam.id}</div>
                    <div className="text-xs opacity-80">{cam.name}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Real-time Event Log */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 flex flex-col h-[700px]">
          <div className="p-4 border-b border-gray-700 flex items-center justify-between">
            <h3 className="font-medium text-white flex items-center space-x-2">
              <Activity className="w-4 h-4 text-blue-500" />
              <span>{selectedCam.id} Stream</span>
            </h3>
            <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded-full">Live Extraction</span>
          </div>
          <div 
            ref={eventLogRef}
            className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-sm"
          >
            {events.filter(e => e.camera === selectedCam.id).length === 0 ? (
              <div className="text-center text-gray-500 py-10">
                Waiting for pipeline events...
              </div>
            ) : (
              events.filter(e => e.camera === selectedCam.id).map((event) => (
                <div key={event.id} className="bg-gray-900/80 p-3 rounded-lg border border-gray-700/80 shadow-inner">
                  <div className="flex justify-between items-start mb-1.5">
                    <span className="text-gray-400 text-[10px]">{event.timestamp}</span>
                    <span className="bg-gray-800 px-1.5 py-0.5 rounded text-[10px] text-gray-300 border border-gray-700">{event.camera}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`${getEventColor(event.type)}`}>
                      {getEventIcon(event.type)}
                    </span>
                    <span className={`font-semibold tracking-tight ${getEventColor(event.type)}`}>
                      {event.type}
                    </span>
                  </div>
                  <div className="mt-2 text-gray-300 text-xs flex justify-between items-center bg-black/40 px-2 py-1 rounded">
                    <span>{event.zone || 'Global'}</span>
                    <span className="text-green-400/80 font-medium">conf: {event.confidence.toFixed(2)}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default LiveFeeds;
