import React, { useState, useRef, useEffect } from 'react';
import { 
  Activity, 
  BarChart3, 
  Layers, 
  Zap, 
  AlertCircle, 
  TrendingUp, 
  Package, 
  Truck, 
  Clock,
  LayoutDashboard,
  Map as MapIcon,
  Shield,
  MessageSquare,
  Navigation,
  Users,
  AlertTriangle,
  ChevronRight,
  Phone,
  Radio,
  Settings,
  AlertOctagon,
  RefreshCcw
} from 'lucide-react';

import { PhoneFrame, Gauge, ActionButton, DataList } from "./renderer/ShiftOpsPrimitives";
import BlueprintProjector from "./BlueprintProjector";

// --- Aegis-Style Product Primitives ---

const StatCard = ({ label, value, trend, color = "blue", icon: Icon }) => (
  <div className="bg-slate-900/50 border border-white/5 p-4 rounded-2xl shadow-xl">
    <div className="flex justify-between items-start mb-2">
      <div className={`p-2 rounded-lg bg-${color}-500/10 text-${color}-400`}>
        {Icon && <Icon size={18} />}
      </div>
      <span className={`text-[10px] font-bold ${trend?.startsWith('+') ? 'text-red-400' : 'text-emerald-400'}`}>
        {trend}
      </span>
    </div>
    <div className="text-2xl font-bold text-white tracking-tight">{value}</div>
    <div className="text-slate-500 text-[9px] uppercase tracking-widest mt-1 font-bold">{label}</div>
  </div>
);

const MiniMap = ({ label }) => (
  <div className="relative w-full h-full bg-slate-950 rounded-xl overflow-hidden border border-white/5 min-h-[200px]">
    <div className="absolute inset-0 opacity-20" 
         style={{ backgroundImage: 'radial-gradient(#334155 1px, transparent 1px)', backgroundSize: '20px 20px' }} />
    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
       <div className="w-32 h-32 bg-blue-500/10 border border-blue-500/20 rounded-full animate-pulse flex items-center justify-center">
          <div className="w-2 h-2 bg-blue-500 rounded-full shadow-[0_0_10px_rgba(59,130,246,1)]" />
       </div>
    </div>
    <div className="absolute top-4 left-4 bg-slate-900/80 backdrop-blur px-3 py-1.5 rounded-lg border border-white/10 text-[8px] font-mono text-white flex items-center gap-2">
       <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
       {label?.toUpperCase() || 'SPATIAL_FEED_ACTIVE'}
    </div>
  </div>
);

const PriorityIncident = ({ title, severity, units }) => (
  <div className={`p-4 rounded-xl border-l-4 ${severity === 'critical' ? 'bg-red-500/5 border-red-500' : 'bg-amber-500/5 border-amber-500'} border border-white/5`}>
    <div className="flex justify-between items-start mb-1">
      <h4 className="text-xs font-bold text-white uppercase tracking-tight">{title}</h4>
      <span className="text-[8px] font-mono text-slate-500 uppercase tracking-widest">Active_Alert</span>
    </div>
    <div className="flex items-center justify-between mt-3">
      <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono">
        <Activity size={12} className="text-blue-500" /> {units} affected_nodes
      </div>
      <ChevronRight size={14} className="text-slate-600" />
    </div>
  </div>
);

const ChatWindow = ({ title }) => (
  <div className="flex flex-col h-full min-h-[250px]">
    <div className="flex-1 space-y-4 p-2 overflow-y-auto custom-scrollbar">
      <div className="flex flex-col items-start">
        <div className="bg-slate-800/50 p-3 rounded-2xl rounded-tl-none text-[10px] text-slate-300 max-w-[80%] uppercase font-mono tracking-tighter">
          System: Monitoring {title}... Nominal flow detected in all primary sectors.
        </div>
      </div>
      <div className="flex flex-col items-end">
        <div className="bg-blue-600 p-3 rounded-2xl rounded-tr-none text-[10px] text-white max-w-[80%] uppercase font-mono tracking-tighter">
          Admin: Confirmed. Proceed with standard operational cycles.
        </div>
      </div>
    </div>
    <div className="p-2 border-t border-white/5 mt-auto">
       <div className="bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-[10px] text-slate-500 uppercase font-mono">
         Input operational command...
       </div>
    </div>
  </div>
);

// --- Telemetry Engine (The Bloodstream) ---

const useTelemetry = (manifest) => {
  const [telemetry, setTelemetry] = useState({});

  useEffect(() => {
    if (!manifest) return;

    // 1. Initial Scan: Find all bindings and initialize data
    const initialData = {};
    const surfaces = manifest.surfaces || [];
    const domainKpis = manifest.domain_data?.kpis || [];
    
    surfaces.forEach(s => {
      s.layers?.forEach(l => {
        l.components?.forEach(c => {
          if (c.binding) {
            const key = c.binding.endpoint;
            const model = c.binding.response_model || {};
            initialData[key] = {};
            Object.keys(model).forEach(field => {
              initialData[key][field] = 0;
            });
          }
        });
      });
    });
    setTelemetry(initialData);

    // 2. Heartbeat: Simulate the data breathing with domain constraints
    const interval = setInterval(() => {
      setTelemetry(prev => {
        const next = { ...prev };
        Object.keys(next).forEach(endpoint => {
          const entry = { ...next[endpoint] };
          Object.keys(entry).forEach(field => {
            const fLow = field.toLowerCase();
            
            // Check for domain KPI match in manifest
            const matchedKpi = domainKpis.find(kpi => kpi.name.toLowerCase().includes(fLow) || fLow.includes(kpi.name.toLowerCase()));
            
            if (matchedKpi && matchedKpi.range) {
              const [min, max] = matchedKpi.range;
              const current = entry[field] || (min + (max - min) / 2);
              const delta = (Math.random() - 0.5) * (max - min) * 0.05;
              entry[field] = Math.min(max, Math.max(min, +(current + delta).toFixed(1)));
            } else if (fLow.includes('rate') || fLow.includes('percentage') || fLow.includes('efficiency')) {
              const current = entry[field] || 85;
              entry[field] = Math.min(100, Math.max(0, +(current + (Math.random() - 0.4)).toFixed(1)));
            } else if (fLow.includes('severity') || fLow.includes('rank')) {
              entry[field] = Math.floor(Math.random() * 10) + 1;
            } else if (fLow.includes('units') || fLow.includes('count')) {
              const current = entry[field] || 5000;
              entry[field] = Math.floor(current + (Math.random() * 10));
            } else if (fLow.includes('timestamp') || fLow.includes('updated')) {
              entry[field] = new Date().toLocaleTimeString();
            } else {
              const time = Date.now() / 2000;
              entry[field] = Math.floor(50 + Math.sin(time) * 20);
            }
          });
          next[endpoint] = entry;
        });
        return next;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [manifest]);

  return telemetry;
};

// --- The Main "Aegis-Grade" Projector ---

export default function SurfaceProjector({ manifest, state: externalState }) {
  const [activeSurfaceId, setActiveSurfaceId] = useState(null);
  
  const surfaces = manifest?.surfaces || (manifest?.layers ? [{
    id: 'default',
    title: manifest.title || "Surface Projection",
    projection: manifest.projection || "dashboard",
    layers: manifest.layers
  }] : []);

  const liveTelemetry = useTelemetry(manifest);

  useEffect(() => {
    if (surfaces.length > 0 && !activeSurfaceId) {
      setActiveSurfaceId(surfaces[0].id);
    }
  }, [surfaces, activeSurfaceId]);

  if (!manifest || surfaces.length === 0) return (
    <div className="flex flex-col items-center justify-center h-full text-slate-600 italic font-mono text-xs gap-4 uppercase tracking-[0.2em]">
      <Zap size={24} className="opacity-20 animate-pulse" />
      Awaiting Surface Projection...
    </div>
  );

  const activeSurface = surfaces.find(s => s.id === activeSurfaceId) || surfaces[0];

  const renderComponent = (comp, i) => {
    let data = {};
    let value = 0;
    let label = comp.label;

    if (comp.binding) {
        data = liveTelemetry[comp.binding.endpoint] || {};
        // Find the most appropriate numeric value for the gauge
        const keys = Object.keys(data);
        const numericKey = keys.find(k => k.toLowerCase().includes('rate') || k.toLowerCase().includes('percent') || k.toLowerCase().includes('efficiency')) || 
                           keys.find(k => typeof data[k] === 'number');
        if (numericKey) value = data[numericKey];
    }

    switch (comp.type) {
      case 'map':
        return <MiniMap key={i} />;
      case 'chat':
        return <ChatWindow key={i} />;
      case 'stat_grid':
        return (
          <div key={i} className="grid grid-cols-2 gap-4">
            <StatCard label="Live Throughput" value={data.units_produced || 12400} trend="+1.2%" icon={Activity} color="blue" />
            <StatCard label="Active Exceptions" value={data.exceptions?.length || 2} trend="-1" icon={AlertTriangle} color="red" />
          </div>
        );
      case 'incidents':
        // Generate Domain-Appropriate Incidents from Manifest
        const domainIncidents = manifest.domain_data?.incidents || [];
        const incident1 = domainIncidents[0]?.type || "System Latency";
        const incident2 = domainIncidents[1]?.type || "Data Gap";
        
        return (
          <div key={i} className="space-y-3">
            <PriorityIncident 
              title={incident1} 
              severity="critical" 
              units={data.units || 4} 
            />
            <PriorityIncident 
              title={incident2} 
              severity="medium" 
              units={data.units || 2} 
            />
          </div>
        );
      case 'metric':
        const kpiInfo = manifest.domain_data?.kpis?.find(k => k.name.toLowerCase() === label.toLowerCase() || label.toLowerCase().includes(k.name.toLowerCase()));
        const unit = kpiInfo?.unit || (label.toLowerCase().includes('rate') || label.toLowerCase().includes('efficiency') || label.toLowerCase().includes('accuracy') || label.toLowerCase().includes('percent') ? "%" : "");
        const range = kpiInfo?.range || [0, 100];
        
        // Dynamic coloring based on range
        let color = 'blue';
        if (unit === "%") {
          if (value < 70) color = 'red';
          else if (value < 90) color = 'orange';
          else color = 'emerald';
        }
        
        return <Gauge key={i} label={label} value={value} unit={unit} color={color} min={range[0]} max={range[1]} />;
      case 'list':
        // Generate mock items using the label context
        const contextLabel = label.split(' ').pop().replace('s', '');
        const mockItems = [
            { id: "ID-001", label: `${contextLabel} #4402`, subtext: "ACTIVE_TRANSIT" },
            { id: "ID-002", label: `${contextLabel} #9910`, subtext: "STAGED" },
            { id: "ID-003", label: `${contextLabel} #1288`, subtext: "PENDING" }
        ];
        return <DataList key={i} title={label} items={mockItems} />;
      case 'action':
        return <ActionButton key={i} label={label} icon={comp.icon} theme={comp.theme} />;
      default:
        return <div key={i} className="text-[10px] text-slate-700 italic border border-dashed border-white/5 p-4 rounded-xl">Unknown Component: {comp.type}</div>;
    }
  };

  const archetype = manifest.domain_data?.archetype || "General Operations";
  const isEmergency = archetype.toLowerCase().includes('emergency') || archetype.toLowerCase().includes('fire') || archetype.toLowerCase().includes('healthcare');

  const renderSurfaceContent = () => {
    if (activeSurface.projection === 'blueprint') {
      return <BlueprintProjector manifest={activeSurface} state={externalState} />;
    }

    const content = (
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Aegis Header */}
        <div className="flex justify-between items-center border-b border-white/5 pb-6">
          <div className="flex items-center gap-4">
            <div className={`p-3 rounded-2xl shadow-lg ${isEmergency ? 'bg-red-600 shadow-red-600/20' : 'bg-blue-600 shadow-blue-600/20'}`}>
              {isEmergency ? <AlertTriangle className="text-white" size={24} /> : <Shield className="text-white" size={24} />}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight uppercase tracking-[0.1em]">{activeSurface.title}</h2>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[8px] text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 animate-pulse uppercase">Systems Optimal</span>
                <span className="text-[8px] text-slate-500 font-mono uppercase tracking-widest">• Mode: {activeSurface.projection}</span>
                <span className="text-[8px] text-slate-500 font-mono uppercase tracking-widest">• Domain: {archetype}</span>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
             <button className="px-4 py-2 bg-slate-900 border border-white/5 rounded-xl text-[10px] font-bold text-slate-400 uppercase tracking-widest hover:text-white transition-all flex items-center gap-2">
                <RefreshCcw size={12} /> Sync Grid
             </button>
             <button className={`px-4 py-2 rounded-xl text-[10px] font-bold text-white uppercase tracking-widest transition-all shadow-lg ${
               isEmergency 
               ? 'bg-red-600 hover:bg-red-500 shadow-red-900/20' 
               : 'bg-slate-800 hover:bg-slate-700 border border-white/10 shadow-black/40'
             }`}>
                {isEmergency ? 'Declare Emergency' : 'System Override'}
             </button>
          </div>
        </div>

        {/* Dynamic Layer Rendering */}
        <div className="grid grid-cols-12 gap-6">
          {activeSurface.layers?.map((layer, li) => (
             <div key={li} className="col-span-12 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {layer.components?.map((comp, ci) => renderComponent(comp, ci))}
                </div>
             </div>
          ))}
        </div>
      </div>
    );

    if (activeSurface.projection === 'mobile') {
      return (
        <div className="py-12 flex justify-center items-center">
          <PhoneFrame title={activeSurface.title}>
            <div className="p-4 space-y-6">
               {activeSurface.layers?.map((layer, li) => (
                 <div key={li} className="space-y-4">
                    {layer.components?.map((comp, ci) => renderComponent(comp, ci))}
                 </div>
               ))}
            </div>
          </PhoneFrame>
        </div>
      );
    }

    return <div className="p-8">{content}</div>;
  };

  return (
    <div className="w-full h-full bg-[#050507] flex flex-col overflow-hidden">
      
      {/* Surface Selector Tabs */}
      {surfaces.length > 1 && (
        <div className="h-10 border-b border-white/5 bg-slate-900/20 flex items-center px-6 shrink-0 gap-4">
          <span className="text-[8px] font-bold text-slate-500 uppercase tracking-widest mr-2">Operational Surfaces:</span>
          {surfaces.map(s => (
            <button 
              key={s.id}
              onClick={() => setActiveSurfaceId(s.id)}
              className={`px-3 py-1 rounded-full text-[9px] font-bold uppercase tracking-wider transition-all ${
                activeSurfaceId === s.id ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' : 'text-slate-500 hover:text-slate-300 bg-white/5'
              }`}
            >
              {s.title}
            </button>
          ))}
        </div>
      )}

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {renderSurfaceContent()}
      </div>
    </div>
  );
}
