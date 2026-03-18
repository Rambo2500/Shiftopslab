import React, { useState, useEffect, useMemo } from 'react';
import SimulationRenderer from "./renderer/SimulationRenderer"
import { intentToModel } from "./intent/intentToModel"
import SurfaceProjector from "./SurfaceProjector";

export default function DeviceCanvas({ prompt }) {
  const [viewMode, setViewMode] = useState('product'); 
  const [manifest, setManifest] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const model = intentToModel(prompt)

  // 1. Optimistic Skeleton Logic
  const skeletonManifest = useMemo(() => {
    const p = prompt?.toLowerCase() || "";
    if (p.includes('ems') || p.includes('dispatch') || p.includes('mobile')) {
      return { projection: 'mobile', title: 'EMS_DISPATCH_BOOTING...' };
    }
    if (p.includes('rocket') || p.includes('blueprint')) return { projection: 'blueprint', title: 'SCHEMATIC_LOAD...' };
    return { projection: 'dashboard', title: 'DASHBOARD_SYNC...' };
  }, [prompt]);

  // 2. The Smart Bridge Call (To Flash Lite via surface_orchestrator.py)
  useEffect(() => {
    if (!prompt) return;
    
    setIsLoading(true);
    setManifest(skeletonManifest);

    const fetchManifest = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8001/project', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt })
        });
        const data = await response.json();
        setManifest(data);
      } catch (err) {
        console.error("Bridge Error: ", err);
      } finally {
        setIsLoading(false);
      }
    };

    const timer = setTimeout(fetchManifest, 150); 
    return () => clearTimeout(timer);
  }, [prompt, skeletonManifest]);

  // EMS-SPECIFIC LIVE TELEMETRY (Mock)
  const mockState = {
    metrics: { 
      active_units: 8, 
      response_time: "4.2", 
      alerts: 2, 
      health: 99, 
      latency: 8, 
      "thrust": "94.2%", 
      "temp": "1,180K" 
    },
    data: {
      units: [
        { id: "AMB-01", label: "Med Unit 01", subtext: "EN_ROUTE_HOSPITAL" },
        { id: "AMB-05", label: "Med Unit 05", subtext: "STATIONED" },
        { id: "AMB-08", label: "Med Unit 08", subtext: "RESPONDING" }
      ],
      fleet: [
        { id: "TRK-09", label: "Route: North Aurora", subtext: "ON_TIME" },
        { id: "TRK-12", label: "Route: West Chicago", subtext: "DELAYED" }
      ]
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#020617] text-white">
      <div className="flex border-b border-slate-800 p-2 space-x-2 bg-slate-950/50">
        <button onClick={() => setViewMode('product')} className={`px-3 py-1 text-[10px] font-bold rounded ${viewMode === 'product' ? 'bg-blue-600' : 'text-slate-500'}`}>
          PRODUCT_SHOWROOM
        </button>
        <button onClick={() => setViewMode('engine')} className={`px-3 py-1 text-[10px] font-bold rounded ${viewMode === 'engine' ? 'bg-slate-700' : 'text-slate-500'}`}>
          ENGINE_ROOM (NODES)
        </button>
        {isLoading && <div className="text-[8px] text-blue-500 font-mono animate-pulse flex items-center ml-auto pr-2">// AI_DESIGNING_SURFACE...</div>}
      </div>

      <div className="flex-1 overflow-hidden relative">
        {viewMode === 'engine' ? (
          <div className="flex flex-col items-center justify-center h-full p-10">
            <div className="mb-4 text-xs font-mono text-blue-500 uppercase tracking-widest animate-pulse">Internal System Graph</div>
            <div className="border border-slate-800 rounded-lg bg-[#0c1424] p-4 shadow-2xl">
              <SimulationRenderer model={model}/>
            </div>
          </div>
        ) : (
          <SurfaceProjector manifest={manifest || skeletonManifest} state={mockState} />
        )}
      </div>

      <div className="p-3 border-t border-slate-800 bg-slate-950 text-[10px] font-mono text-slate-500 flex justify-between">
        <span className="truncate pr-4">DEMO_INTENT: "{prompt || 'EMS_GATEWAY_DEFAULT'}"</span>
        <span className="text-blue-900 uppercase shrink-0">ShiftOps-OS_Surface_{manifest?.projection || 'PENDING'}</span>
      </div>
    </div>
  )
}

